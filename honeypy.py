import argparse
import honeypot
from web_honeypot import run_web_honeypot


def main():
    parser = argparse.ArgumentParser(description="SSH / HTTP Honeypot")

    parser.add_argument('-a', '--address', type=str, required=True, help="Bind address")
    parser.add_argument('-p', '--port', type=int, required=True, help="Port number")
    parser.add_argument('-u', '--username', type=str, help="Username")
    parser.add_argument('-pw', '--password', type=str, help="Password")

    parser.add_argument('-s', '--ssh', action='store_true', help="Start SSH honeypot")
    parser.add_argument('-w', '--http', action='store_true', help="Start HTTP honeypot")

    args = parser.parse_args()

    try:
        if args.ssh:
            print("[-] Starting SSH Honeypot...")

            username = args.username if args.username else None
            password = args.password if args.password else None

            honeypot.honeypot(
                args.address,
                args.port,
                username,
                password
            )

        elif args.http:
            print("[-] Starting HTTP Honeypot...")

            username = args.username if args.username else "admin"
            password = args.password if args.password else "password"

            print(f"Port: {args.port} | Username: {username} | Password: {password}")

            run_web_honeypot(args.port, username, password)

        else:
            print("[-] Please specify a honeypot type: --ssh or --http")

    except KeyboardInterrupt:
        print("\n[!] Shutting down honeypot...\n")
    except Exception as e:
        print(f"[!] Error: {e}")


if __name__ == "__main__":
    main()
