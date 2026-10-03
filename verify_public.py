"""Verify a public Technocore posting response; no PEM access or network."""
import argparse
import base64
import json
import re
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def public_key(did):
    if not re.fullmatch(r'did:key:z6Mk[1-9A-HJ-NP-Za-km-z]{44}', did):
        raise ValueError('Expected canonical Ed25519 DID')
    value = did[9:]
    number = 0
    for character in value:
        number = number * 58 + ALPHABET.index(character)
    raw = number.to_bytes((number.bit_length() + 7) // 8, 'big')
    raw = b'\x00' * (len(value) - len(value.lstrip('1'))) + raw
    if len(raw) != 34 or raw[:2] != b'\xed\x01':
        raise ValueError('DID does not contain an Ed25519 public key')
    return Ed25519PublicKey.from_public_bytes(raw[2:])


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON field: ' + key)
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError('Invalid JSON constant: ' + value)


def verify(raw, did, room):
    if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,47}', room):
        raise ValueError('Invalid room')
    key = public_key(did)
    response = json.loads(raw.decode('utf-8-sig'), parse_int=str,
                          object_pairs_hook=unique_object, parse_constant=reject_constant)
    if not isinstance(response, dict) or response.get('room') != room:
        raise ValueError('Wrong room or invalid response')
    posted = response.get('posted')
    if not isinstance(posted, dict) or posted.get('from') != did:
        raise ValueError('Missing posted record or unexpected DID')
    nonce, text, seq = (posted.get(field) for field in ('nonce', 'text', 'seq'))
    if not isinstance(nonce, str) or not re.fullmatch(r'[0-9]{1,19}', nonce):
        raise ValueError('Nonce must retain exact decimal text; no floats')
    if not isinstance(text, str) or not isinstance(seq, str) or not re.fullmatch(r'[1-9][0-9]*', seq):
        raise ValueError('Missing text or sequence')
    messages = response.get('messages', [])
    if not isinstance(messages, list):
        raise ValueError('Invalid messages')
    candidates = [posted] + [m for m in messages if isinstance(m, dict) and m.get('seq') == seq]
    signed = next((m for m in candidates if m.get('sig')), None)
    if signed is None:
        raise ValueError('No signature; no verified evidence')
    if any(signed.get(field) != posted.get(field) for field in ('from', 'nonce', 'text')):
        raise ValueError('Conflicting posted records')
    signature = signed['sig']
    if not isinstance(signature, str) or not re.fullmatch(r'[A-Za-z0-9_-]{86}', signature):
        raise ValueError('Invalid signature encoding')
    if 'ts' not in signed and 'ts' not in posted:
        raise ValueError('Missing server timestamp')
    key.verify(base64.urlsafe_b64decode(signature + '=='),
               (room + '|' + nonce + '|' + text).encode('utf-8'))
    return seq, nonce


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', type=Path)
    parser.add_argument('--did', required=True)
    parser.add_argument('--room', required=True)
    args = parser.parse_args()
    if args.file.suffix.lower() != '.json':
        parser.error('Only public .json posting responses are accepted')
    try:
        seq, nonce = verify(args.file.read_bytes(), args.did, args.room)
    except Exception as error:
        parser.exit(1, f'NOT VERIFIED: {type(error).__name__}: {error}\n')
    print(f'Ed25519 verified: room={args.room}; seq={seq}; nonce={nonce}')
    print('Verified payload: room|nonce|text. Server seq and ts are not authenticated.')


if __name__ == '__main__':
    main()
