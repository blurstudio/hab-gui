import hab_gui.utils


def test_exec_obj():
    class ExecBoth:
        def exec_(self):
            return "exec_"

        def exec(self):
            return "exec"

    class Exec_:
        def exec_(self):
            return "exec_"

    class Exec:
        def exec(self):
            return "exec"

    assert hab_gui.utils.exec_obj(ExecBoth()) == "exec"
    assert hab_gui.utils.exec_obj(Exec_()) == "exec_"
    assert hab_gui.utils.exec_obj(Exec()) == "exec"
