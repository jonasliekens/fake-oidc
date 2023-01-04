import json
import logging

from flask import Flask, Response, request, abort, redirect, render_template

import config
from oidc import generate_id_token
from users import find_all_user_tokens_and_details, find_user_by_token
from utils import random_string

app = Flask(__name__)
# Used to keep state codes clients are sending
state_dict = {}
# Used to keep auth codes to be traded for absolutely very safe, CIA unbreakable, FBI baffling, Gov. denying JWT tokens.
code_dict = {}


@app.route('/')
def oh_wow_a_duck():
    logging.info("🦆 Quack! 🦆")
    return 'Wow! Such Security! Much Safe! So tight!'


@app.route('/.well-known/openid-configuration')
def get_openid_config():
    logging.info("📖 Returning OIDC config for {}".format(config.hostname))
    return new_json_response(
        {
            'issuer': config.hostname,
            'authorization_endpoint': '{}/login'.format(config.hostname),
            'token_endpoint': '{}/token'.format(config.hostname),
            'userinfo_endpoint': '{}/user-info'.format(config.hostname),
            'end_session_endpoint': '{}/logout'.format(config.hostname),
            'jwks_uri': '{}/certs'.format(config.hostname)
        }
    )


@app.route('/certs')
def get_jwk():
    logging.info("🔓 returning encryption info")
    jwk_data = json.loads(config.jwk.export_public())
    jwk_data['alg'] = 'RS256'
    jwk_keys = {
        'keys': [
            jwk_data
        ]
    }
    return new_json_response(jwk_keys)


@app.route('/login', methods=['GET', 'POST'])
def login():
    logging.info("👀 Validating login request very strictly. I swear!")
    if request.method == 'GET':
        if 'redirect_uri' not in request.args:
            return login_page_with_error("Missing 'redirect_uri' query parameter")
        if 'state' not in request.args:
            return login_page_with_error("Missing 'state' query parameter")
        if 'client_id' not in request.args:
            return login_page_with_error("Missing 'client_id' query parameter")
        if 'scope' not in request.args:
            return login_page_with_error("Missing 'scope' query parameter.")
        if not request.args['scope'].__contains__('openid'):
            return login_page_with_error("'scope' must contain value 'openid'")

        state = request.args['state']

        state_dict.update({
            state: {
                'redirect_uri': request.args['redirect_uri'],
                'nonce': request.args['nonce'] if 'nonce' in request.args else None,
                'client_id': request.args['client_id'],
                'scope': request.args['scope']
            }
        })

        logging.info("👋 returning Login form")

        token_user_map = find_all_user_tokens_and_details()
        return render_template('login.html',
                               state=state,
                               options=[{'key': k, 'value': v['name']} for k, v in token_user_map.items()])

    if request.method == 'POST':
        code, redirect_uri, state_id = register_new_code(
            request.form['state'] if 'state' in request.form else abort_with_bad_request('Missing state argument'),
            request.form['token'] if 'token' in request.form else abort_with_bad_request('No user selected')
        )

        logging.info("✔️ Everything looks fine, redirecting to {}".format(redirect_uri))
        return redirect('{}?code={}&state={}'.format(redirect_uri, code, state_id))


@app.route('/token', methods=['POST'])
def get_token():
    code = request.form['code']
    if not code:
        return abort(401)

    if code not in code_dict.keys():
        return abort(401)

    token_data = code_dict[code]
    del code_dict[code]

    return new_json_response(
        {
            'access_token': token_data['access_token'],
            'token_type': 'bearer',
            'expires_in': config.token_validity,
            'scope': token_data['scope'],
            'id_token': generate_id_token(token_data).serialize()
        }
    )


@app.route('/user-info', methods=['GET'])
def get_user_principal():
    if 'Authorization' not in request.headers.keys():
        abort(401)

    principal = find_user_by_token(request.headers['Authorization'].split(' ')[1])

    if not principal:
        abort(401)

    return new_json_response(principal)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if 'post_logout_redirect_uri' in request.args.keys():
        return redirect(request.args['post_logout_redirect_uri'])
    return Response()


def new_json_response(payload):
    return Response(json.dumps(payload), mimetype='application/json')


def register_new_code(state_id, token):
    state = state_dict[state_id] if state_id in state_dict \
        else abort_with_bad_request('State unknown. Please call mr. president')
    code = random_string()

    code_dict[code] = {
        'nonce': state['nonce'],
        'scope': state['scope'],
        'client_id': state['client_id'],
        'access_token': token,
    }

    del state_dict[state_id]

    return code, state['redirect_uri'], state_id


def abort_with_bad_request(log_msg):
    logging.info('🚫 {}'.format(log_msg))
    abort(400)


def login_page_with_error(error_msg):
    logging.info('🚫 {}'.format(error_msg))
    return render_template('login.html',
                           error='🚫 {}'.format(error_msg))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
