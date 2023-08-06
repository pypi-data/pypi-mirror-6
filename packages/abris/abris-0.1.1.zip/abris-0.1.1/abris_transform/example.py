from StringIO import StringIO

from abris_transform.abris import Abris


def main():
    with open("config.json", "r") as config_file:
        cochlea = Abris(config_file)

    initial_data = "10,Spain,3.5,True\n" \
                   "12,France,2.5,True\n" \
                   "14,Germany,10.5,False"

    data = cochlea.fit_transform(StringIO(initial_data))
    print data

    new_data = "10,Spain,1,True\n" \
               "10,France,20,False"
    transformed_data = cochlea.transform(StringIO(new_data))
    print transformed_data


if __name__ == "__main__":
    main()
