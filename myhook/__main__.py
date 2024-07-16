from .my_hook import MyHook


def main():
    my_hook = MyHook()
    print(my_hook.key_binding_status())
    my_hook.start_hooking()


main()

