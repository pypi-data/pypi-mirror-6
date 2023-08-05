import logical_rules

def test_is_pizza(word):
    if word == "pizza":
        return True
    return False
logical_rules.site.register("test_is_pizza", test_is_pizza)
