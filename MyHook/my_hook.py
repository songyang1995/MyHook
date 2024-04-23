import os

import PyHook3
import pythoncom
import win32api
import yaml

from . import simple_features, base_feature, win_features


class MyHook:
    def __init__(self, config_path="hotkey_map.yml"):

        self._key_map = dict()  # {key:(feature,keep_old_key)}
        self._stop_hooking_feature = simple_features.RunCallable(self._stop_hooking)
        self.stop_hooking_feature_binded_status = False

        self.config = self._init_config(config_path)
        self.hook_manager = PyHook3.HookManager()
        self._init_feature_binding()
        self._init_hotkey_binding()
        self._init_command_binding()

    @staticmethod
    def _init_config(config_path: str) -> dict:
        assert os.path.isfile(config_path)
        try:
            with open(config_path, "r", encoding="utf8") as f:
                config = yaml.safe_load(f)
                return config
        except IOError:
            raise IOError(f"配置文件 f{config_path} 读取失败")

    def _atomic_bind_key(self, key_code: str, feature: base_feature.BaseFeature, keep_old_key: bool):
        if key_code in self._key_map:
            raise KeyError(f"按键已被分配：{key_code} -> {self._key_map[key_code][0]}")
        else:
            self._key_map[key_code] = (feature, keep_old_key)

    def _init_feature_binding(self):
        assert "feature_binding" in self.config
        for key_code in self.config["feature_binding"]:

            feature_desc: str = self.config["feature_binding"][key_code]
            # parse feature_desc into feature and keep_old_key
            if len(feature_desc.split("|")) == 2:
                feature_cls_name, keep_old_key = feature_desc.split("|")
                feature_cls_name = feature_cls_name.strip()
                assert keep_old_key in ("False", "True")
                keep_old_key: bool = keep_old_key == "True"
            elif len(feature_desc.split("|")) == 1:
                feature_cls_name, keep_old_key = feature_desc.strip(), False
            else:
                raise ValueError(f"配置项出错：feature_binding->{key_code}->{feature_desc}")
            # find feature_class and create feature instance
            if feature_cls_name in win_features.__dict__ and issubclass(win_features.__dict__[feature_cls_name], win_features.BaseFeature):
                # 找到对应的类
                feature: base_feature.BaseFeature = win_features.__dict__[feature_cls_name]()
            elif feature_cls_name in globals().keys() and issubclass(globals()[feature_cls_name], win_features.BaseFeature):
                feature: base_feature.BaseFeature = globals()[feature_cls_name]()
                # TODO: unit test
            elif feature_cls_name == "StopHooking":
                feature = self._stop_hooking_feature
                self.stop_hooking_feature_binded_status = True
            else:
                raise ValueError(f"未知命令:{feature_cls_name}")
            self._atomic_bind_key(key_code, feature, keep_old_key)

    def _init_hotkey_binding(self):
        if ("hotkey_binding" not in self.config) or self.config["hotkey_binding"] is None or len(self.config["hotkey_binding"]) == 0:
            return
        for key_code in self.config["hotkey_binding"]:
            new_key: str = self.config["hotkey_binding"][key_code]
            feature = simple_features.Hotkey(new_key)
            self._atomic_bind_key(key_code, feature, False)

    def _init_command_binding(self):
        if "command_binding" not in self.config or self.config["command_binding"] is None or len(self.config["command_binding"]) == 0:
            return
        for key_code in self.config["command_binding"]:
            command: str = self.config["command_binding"][key_code]
            feature = simple_features.RunCommand(command)
            self._atomic_bind_key(key_code, feature, False)

    def manual_binding(self, key: str, feature: base_feature.BaseFeature, keep_old_key: bool):
        try:
            self._atomic_bind_key(key, feature, keep_old_key)
        except KeyError as e:
            print(e.args[0])

    def _confirm_stop_hooking_was_binded(self):
        if not self.stop_hooking_feature_binded_status:
            self._atomic_bind_key("Snapshot", self._stop_hooking_feature, False)

    def on_keyboard_event(self, event: PyHook3.KeyboardEvent):
        """监听函数"""

        if event.Key in self._key_map and not event.Injected:  # 该按键已被监听且是原生键盘事件，防止热键传递
            feature, keep_old_key = self._key_map[event.Key]
            feature()
            return keep_old_key
        # 其他情况不捕捉按键事件
        return True

    def start_hooking(self):
        self._confirm_stop_hooking_was_binded()
        self.hook_manager.KeyDown = self.on_keyboard_event
        self.hook_manager.HookKeyboard()
        pythoncom.PumpMessages()

    def _stop_hooking(self):
        win32api.PostQuitMessage()
        self.hook_manager.UnhookKeyboard()

    def key_binding_status(self):
        """描述按键绑定状态"""
        key_bind_str = "key Mapping:{\n"
        for key in self._key_map:
            feature, keep_old_key = self._key_map[key]
            feature: base_feature.BaseFeature
            key_bind_str += f"  {key:<10} -> {feature.get_description():　<20}, {'保留原按键' if keep_old_key else '不保留原按键'},\n"

        key_bind_str += "}"
        return key_bind_str


def main():
    my_hook = MyHook()
    print(my_hook.key_binding_status())
    my_hook.start_hooking()


if __name__ == "__main__":
    main()
