import micropython
from classes.app_manager import ApplicationManager

@micropython.native
def main():
    micropython.alloc_emergency_exception_buf(100)
   
    try:
        app = ApplicationManager()
        app.initialize()
        app.run()
    except Exception as e:
        print("An unexpected error occurred: ", e)
    except KeyboardInterrupt:
        pass
    finally:
        app.stop()

if __name__ == "__main__":
    main()