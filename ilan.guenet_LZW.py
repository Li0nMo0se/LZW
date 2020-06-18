import argparse
import pandas as pd


def uncompress(file, dic):
    """
    Uncompress a file with an initial dictionary
    :param file: file to decompress
    :param dic: initial dictionary
    :return: the string corresponding to the uncompression of the file
    """
    pass


def compress(file):
    """
    Compress a file (its content)
    :param file: file to compress
    :return: list of address (integers) which represents the output
    """

    def make_dico(file):
        dico_set = set()
        for c in file:
            dico_set.add(c)
        dico_set.add('%')
        dico = list(dico_set)
        dico.sort()
        return dico

    dico = make_dico(file)

    curr_addr = len(dico)
    output = "I AM AN INVALID OUTPUT!"
    df = pd.DataFrame(columns=['Buffer', 'Input', 'New sequence', 'Address',
                               'Output'])
    df_i = 0
    for c in file:  # foreach input character in the file
        #  TODO
        input = c
        buffer = c
        new_seq = ''
        addrr = curr_addr
        output_local = f"@[{input}]"
        df.loc[df_i] = [input, buffer, new_seq, addrr, output_local]
        df_i += 1

    return output, df, dico


def process_compression_results(filename, output, df, dico):
    # Get the prefix of the file name
    prefix = filename[filename.rfind('/') + 1:]
    prefix = prefix[:-4]  # avoid .txt extension

    # Save LZW table
    table_file = prefix + '_LZWtable.csv'
    df.to_csv(table_file, index=False)

    # Save dico
    df_dico = pd.DataFrame(columns=dico)
    dico_file = prefix + '_dico.csv'
    df_dico.to_csv(dico_file)

    # Save the output of the compression
    output_file = prefix + '.lzw'
    output_file = open(output_file, "w")
    output_file.write(output)
    output_file.close()


def get_dictionary_from_csv(file):
    """
    Get the dictionary from a csv file
    :param file: .txt file corresponding to the csv file
    :return: list of words in the dictionary
    """
    csv_file = file[:-4]  # avoid .txt extension
    csv_file += "_dico.csv"
    dic = pd.read_csv(csv_file, delimiter=',')
    return list(dic.columns)


def get_file_content(filename):
    """
    Get the whole content of a file.
    :param filename:
    :return: return a string with the content of the file
    """
    fp = open(filename, "r")
    file_content = fp.read()
    fp.close()

    # if the last character is an end of line, remove it
    if file_content[-1] == '\n':
        file_content = file_content[:-1]
    return file_content


if __name__ == '__main__':
    #  parse command line
    parser = argparse.ArgumentParser(description='LZW compression and '
                                                 'decompression')
    parser.add_argument('-p', type=str, nargs=1, help="path to the file to "
                                                      "process")
    parser.add_argument('-c', action='store_true', help="Compress a file")
    parser.add_argument('-u', action='store_true', help="Uncompress a file")

    args = parser.parse_args()
    filename = args.p[0]

    #  Process the file
    if args.c:
        # Get the whole content of the file
        file_content = get_file_content(filename)
        output, df_res, dico_res = compress(file_content)
        process_compression_results(filename, output, df_res, dico_res)

    if args.u:
        # Get the initial dictionary
        dic = get_dictionary_from_csv(filename)
        # Get the string to uncompress
        file_content = get_file_content(filename)
        uncompress(file_content, dic)
