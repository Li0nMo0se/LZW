import argparse
import pandas as pd


def size_in_bits(nb):
    return nb.bit_length()


def read_addr_n_bits(input, size):
    res = input[:size]
    return int(res, 2)


def write_addr_n_bits(addr, size):
    res = str(bin(addr)[2:])
    padding = size - len(res)
    zeros = '0'*padding
    res = zeros + res
    return res


def uncompress(file, dico, special_character='%'):
    """
    Uncompress a file with an initial dictionary
    :param file: file to decompress
    :param dico: initial dictionary
    :return: the string corresponding to the uncompression of the file
    """
    max_addr = len(dico) - 1
    addr_size = size_in_bits(max_addr)
    output = ''
    df = pd.DataFrame(columns=['Buffer', 'Input', 'New sequence', 'Address',
                               'Output'])
    buffer = ''
    df_i = 0
    while file:
        addr = read_addr_n_bits(file, addr_size)
        file = file[addr_size:]
        input = dico[addr]
        if special_character in input:
            # increase the size by the number of special character
            addr_size += len(input)
            input_print = f"@D[{input}]={addr}"
            df.loc[df_i] = [buffer, input_print, '', '', '']
            df_i += 1
        else:
            new_seq = buffer + input[0]

            if new_seq in dico:
                input_print = f"@D[{input}]={addr}"
                df.loc[df_i] = [buffer, input_print, '', '', '']
                df_i += 1
                buffer += new_seq
            else:
                dico.append(new_seq)
                max_addr += 1

                buffer = new_seq[-1:] + input[1:]
                output_local = new_seq[:-1]

                input_print = f"@D[{input}]={addr}"
                df.loc[df_i] = [buffer, input_print, new_seq, max_addr,
                                output_local]
                df_i += 1
                output += output_local

    # No more character available. Hence empty the buffer
    df.loc[df_i] = [buffer, '', '', '', buffer]
    df_i += 1
    output += buffer

    print(df)
    print(output)
    return output


def make_dico(file, special_character='%'):
    dico_set = set()
    for c in file:
        dico_set.add(c)
    dico_set.add(special_character)
    dico = list(dico_set)
    dico.sort()
    return dico


def compress(file, special_character='%'):
    """
    Compress a file (its content)
    :param file: file to compress
    :param special_character:
    :return: list of address (integers) which represents the output
    """

    def check_size_address(addr_output, curr_size, output):
        addr_size = size_in_bits(addr_output)
        delta_size = addr_size - curr_size

        if delta_size > 0:
            addr_special_character = dico.index(special_character)
            df.loc[df_i - 1]['Output'] = \
                f"@[{special_character * delta_size}]=" \
                f"{addr_special_character * delta_size}"

            for i in range(delta_size):
                output += write_addr_n_bits(addr_special_character, curr_size)

        return delta_size, output


    dico = make_dico(file, special_character)

    addr = len(dico)
    output = ''
    df = pd.DataFrame(columns=['Buffer', 'Input', 'New sequence', 'Address',
                               'Output'])

    curr_size = size_in_bits(addr - 1)
    df_i = 0
    buffer = ''
    for input in file:  # foreach input character in the file

        new_seq = buffer + input
        if new_seq in dico:
            df.loc[df_i] = [buffer, input, '', '', '']
            buffer = new_seq
        else:  # the new sequence does not exist in the dictionary
            # Update dico
            dico.append(new_seq)
            output_local = new_seq[:-1]  # all except last character
            addr_output = dico.index(output_local)

            # Check size of the address
            delta_size, output = check_size_address(addr_output, curr_size,
                                                  output)
            if delta_size > 0:
                curr_size += delta_size

            # update table
            output_local = f"@[{output_local}]={addr_output}"
            df.loc[df_i] = [buffer, input, new_seq, addr, output_local]
            addr += 1
            buffer = new_seq[-1]

            # Update output
            output += write_addr_n_bits(addr_output, curr_size)

        df_i += 1

    # no more characters. Empty the buffer now
    assert (buffer in dico)

    addr_output = dico.index(buffer)
    delta_size, output = check_size_address(addr_output, curr_size, output)
    if delta_size > 0:
        curr_size += delta_size

    output_local = f"@[{buffer}]={addr_output}"
    df.loc[df_i] = [buffer, '', '', '', output_local]
    df_i += 1
    output += write_addr_n_bits(addr_output, curr_size)

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
