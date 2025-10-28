from backend.src.integration.client import APICallingException

def main():
    print("Hello from itmo-moodle-agent!")


if __name__ == "__main__":
    main()
    try: 
        raise APICallingException("An error occurred while calling the API.")
    except APICallingException as e:
        print(f"Caught an exception: {e}, Code: {e.code}")
