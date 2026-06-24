def verify_environment():
    """
    Checks all required libraries are importable and prints their versions.
    Returns True if all imports succeed, False if any fail.
    """
    libraries = {
        "numpy": "np",
        "pandas": "pd",
        "scipy": "scipy",
        "simpy": "simpy",
        "gymnasium": "gymnasium",
        "stable_baselines3": "stable_baselines3",
        "requests" : "requests",
        "bs4": "bs4",
        "lxml": "lxml",
        "urllib" : "urllib",
        "json" : "json",
        "re" : "re"
    }

    all_good = True

    for lib, alias in libraries.items():
        try:
            module = __import__(lib)
            version = getattr(module, "__version__", "version unavailable")
            print(f"{lib}: {version}")
        except ImportError:
            print(f"MISSING: {lib}")
            all_good = False

    if all_good:
        print("\n--All libraries imported successfully!--\n\n")
    else:
        print("\n--Some libraries are missing - check your environment.--\n\n")

    return all_good


if __name__ == "__main__":
    verify_environment()