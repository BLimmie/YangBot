import itertools

class message_author:
    def __init__(self, message, author, debug):
        self.message = message
        self.author = author
        self.debug = debug

    def __eq__(self, other):
        if self.debug:
            return self.message.lower() == other.message.lower()
        else:
            return self.message.lower() == other.message.lower() and self.author != other.author

    def __ne__(self, other):
        if self.debug:
            return (self.message.lower() != other.message.lower())
        else:
            return (self.message.lower() != other.message.lower()) or (self.author == other.author)


class message_author_debug:
    """ignores author ID to allow an individual user to test the function"""
    def __init__(self, message, author):
        self.message = message
        self.author = author

    def __eq__(self, other):
        return self.message.lower() == other.message.lower()

    def __ne__(self, other):
        return (self.message.lower() != other.message.lower())


def is_repeat(message_list, n):
    if len(message_list) != n:
        return False
    first = message_list[0]

    if any(a!=b for a,b in itertools.combinations(message_list,2)):
        return False
    return True

def cycle(message_list, msg, n):
    if len(message_list) == n:
        message_list.pop(0)
    elif len(message_list) > n:
        # This should never happen, but we'll add a case for it
        while(len(message_list) > n-1):
            message_list.pop(0)
    message_list.append(msg)

def flush(message_list):
    message_list.clear()

if __name__ == "__main__":
    print("testing equality")
    a = message_author("1", 1)
    b = message_author("1", 1)

    print("Test Equals {}".format("passed" if (a == b) == False else "failed"))

    class test_class:
        def __init__(self):
            self.test_list_1 = [message_author("1", 1), message_author("1", 2), message_author("1", 3), message_author("1", 4)]
            self.test_list_2 = [message_author("1", 1), message_author("1", 2), message_author("2", 3), message_author("1", 4)]
            self.test_list_3 = [message_author("1", 1), message_author("1", 2), message_author("1", 2), message_author("1", 3)]
            self.test_list_short = [message_author("1", 1), message_author("1", 2), message_author("1", 3)]
    print("Testing is_repeat")

    test = test_class()
    n = 4
    print("Test 1 {}".format("passed" if is_repeat(test.test_list_1, n) == True else "failed"))
    print("Test 2 {}".format("passed" if is_repeat(test.test_list_2, n) == False else "failed"))
    print("Test 3 {}".format("passed" if is_repeat(test.test_list_3, n) == False else "failed"))
    print("Test Short {}".format("passed" if is_repeat(test.test_list_short, n) == False else "failed"))

    print("")
    print("Testing cycle")
    test_list_2 = test.test_list_2
    cycle(test.test_list_2, message_author("1", 5), 4)
    cycle(test.test_list_short, message_author("1", 5), 4)
    print("Test cycle max {}".format("passed" if test.test_list_2 == [message_author("1", 2), message_author("2", 3), message_author("1", 4), message_author("1", 5)] else "failed"))
    print("Test cycle append {}".format("passed" if test.test_list_short == [message_author("1", 1), message_author("1", 2), message_author("1", 3), message_author("1", 5)] else "failed"))

    print("")
    print("Testing flush")
    flush(test.test_list_1)
    print("Test flush {}".format("passed" if test.test_list_1 == [] else "failed"))