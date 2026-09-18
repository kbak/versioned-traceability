def pytest_collection_modifyitems(items):
    for item in items:
        for marker in item.iter_markers(name="oft_id"):
            for identifier in marker.args:
                item.user_properties.append(("oft_id", identifier))
