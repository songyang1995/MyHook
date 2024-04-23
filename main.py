from MyHook import MyHook


def main():
    my_hook = MyHook()
    # 可以自定义绑定一些东西
    # 如： my_hook.manual_binding("A", RunCallable(lambda: print("hello world!")),False)
    print(my_hook.key_binding_status())
    my_hook.start_hooking()


if __name__ == "__main__":
    main()
