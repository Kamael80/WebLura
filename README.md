# WebLura Protocol Specification v0.1

> A lightweight, decentralized, end-to-end encrypted messaging protocol with personalized addressing.

---

## What is WebLura?

WebLura is an open messaging protocol designed to be:

- **Minimal** — simple message structure, no bloat
- **Decentralized** — anyone can self-host a WebLura server
- **End-to-end encrypted** — only sender and recipient can read messages
- **Personal** — users choose their own address separator symbol

---

## Address Format

WebLura addresses follow this structure:

```
username{symbol}domain.com
```

The `{symbol}` is chosen by the user at registration from the allowed symbols list. This means two people on the same server can have different address styles.

### Examples

```
kamael⃤lura.com
alice~coolserver.net
bob!mymailhost.org
```

### Allowed Symbols

Users may pick **one** of the following symbols for their address:

| Symbol | Name |
|--------|------|
| ⃤ | Triangle |
| ~ | Tilde |
| ! | Exclamation |
| * | Asterisk |
| ^ | Caret |
| % | Percent |
| & | Ampersand |
| = | Equals |
| + | Plus |
| ? | Question mark |
| > | Chevron |
| § | Section |
| ¤ | Currency |
| ° | Degree |
| • | Bullet |

### Normalization

When routing, servers strip the symbol and resolve only `username` + `domain.com`. This means:

- `kamael⃤lura.com` and `kamael~lura.com` **cannot both exist** — the username `kamael` on `lura.com` is unique regardless of symbol.
- The symbol is purely cosmetic and part of the user's identity/style.

---

## Message Structure

Messages are transmitted as **JSON** over HTTPS. A message object looks like this:

```json
{
  "wlp_version": "0.1",
  "id": "uuid-v4-here",
  "from": "kamael⃤lura.com",
  "to": "alice~coolserver.net",
  "timestamp": "2026-03-20T12:00:00Z",
  "subject_encrypted": "base64-encoded-encrypted-string",
  "body_encrypted": "base64-encoded-encrypted-string",
  "sender_public_key": "base64-encoded-public-key",
  "signature": "base64-encoded-signature"
}
```

### Fields

| Field | Description |
|-------|-------------|
| `wlp_version` | Protocol version |
| `id` | Unique message ID (UUID v4) |
| `from` | Sender's full WebLura address |
| `to` | Recipient's full WebLura address |
| `timestamp` | ISO 8601 send time (UTC) |
| `subject_encrypted` | Encrypted subject line |
| `body_encrypted` | Encrypted message body |
| `sender_public_key` | Sender's public key for verification |
| `signature` | Message signature to verify authenticity |

---

## Encryption

WebLura uses **asymmetric encryption** (public/private key pairs) for E2E encryption.

### Key Generation

When a user registers, the server generates:
- A **public key** — stored on the server, shared openly
- A **private key** — stored only on the client, never sent to the server

### Sending a Message

1. Sender fetches recipient's **public key** from their server
2. Sender encrypts subject + body using recipient's public key
3. Sender signs the message with their own **private key**
4. Encrypted message is sent to recipient's server

### Receiving a Message

1. Recipient fetches the message from their server
2. Recipient decrypts using their own **private key**
3. Recipient verifies the signature using sender's public key

### Algorithm

- **Encryption:** RSA-OAEP with 2048-bit keys (or X25519 in future versions)
- **Signing:** RSA-PSS
- **Hashing:** SHA-256

---

## Server Discovery

WebLura uses **DNS SRV records** for server discovery, similar to SHARP.

To make your server discoverable, add this SRV record to your domain:

```
_weblura._tcp.yourdomain.com. 86400 IN SRV 10 0 8765 yourdomain.com.
```

Replace `yourdomain.com` with your domain and `8765` with your server's port.

---

## Server API Endpoints

A WebLura server must expose the following HTTP endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/.well-known/weblura` | Server info + public key |
| `GET` | `/users/{username}/pubkey` | Get a user's public key |
| `POST` | `/messages/send` | Send a message to a local user |
| `GET` | `/messages/inbox` | Fetch inbox (authenticated) |
| `POST` | `/users/register` | Register a new user |

---

## Server Info Endpoint

`GET /.well-known/weblura` returns:

```json
{
  "protocol": "weblura",
  "version": "0.1",
  "domain": "lura.com",
  "server_software": "weblura-python/0.1"
}
```

---

## Reference Implementation

The official reference server is written in **Python** using **FastAPI**.

> Coming soon — repository link here.

---

## Roadmap

- [ ] v0.1 — Core spec (this document)
- [ ] v0.2 — Attachments support
- [ ] v0.3 — Read receipts
- [ ] v0.4 — X25519 encryption upgrade
- [ ] v1.0 — Stable spec, open for other implementations

---

## Contributing

WebLura is open source and welcomes contributions. Feel free to open issues or pull requests.

---

*WebLura Protocol — made by Kamael / Lura Network*
