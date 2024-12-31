
def main(a):
    def inner():
        print(locals())
        print(locals().__setitem__('a', 2))
        print(locals())

        
    inner()
    print(a)
    
if __name__ == "__main__":
    main(1)