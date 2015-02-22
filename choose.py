import json

def main():
    with open("input.txt", "r") as f:
        data = json.load(f)
    data = sorted(data.keys(), key=lambda k: (len(data[k]), k) )
    for node in data:
        print(node)

if __name__ == "__main__":
    main()

