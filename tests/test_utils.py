def test_path():
    from mas.utils.path import relative_to_root, relative_parent_to_root
    print(relative_to_root(__file__))
    print(relative_parent_to_root(__file__, "tools", "data.json"))