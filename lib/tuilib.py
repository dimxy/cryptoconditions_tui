from lib import rpclib
import json
import time
import readline


def colorize(string, color):

    colors = {
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'green': '\033[92m',
        'red': '\033[91m'
    }
    if color not in colors:
        return string
    else:
        return colors[color] + string + '\033[0m'


def rpc_connection_tui():
    # TODO: possible to save multiply entries from successfull sessions and ask user to choose then
    while True:
        restore_choice = input("Do you want to use connection details from previous session? [y/n]: ")
        if restore_choice == "y":
            try:
                with open("connection.json", "r") as file:
                    connection_json = json.load(file)
                    rpc_user = connection_json["rpc_user"]
                    rpc_password = connection_json["rpc_password"]
                    rpc_port = connection_json["rpc_port"]
                    rpc_connection = rpclib.rpc_connect(rpc_user, rpc_password, int(rpc_port))
            except FileNotFoundError:
                print(colorize("You do not have cached connection details. Please select n for connection setup", "red"))
            break
        elif restore_choice == "n":
            rpc_user = input("Input your rpc user: ")
            rpc_password = input("Input your rpc password: ")
            rpc_port = input("Input your rpc port: ")
            connection_details = {"rpc_user": rpc_user,
                                  "rpc_password": rpc_password,
                                  "rpc_port": rpc_port}
            connection_json = json.dumps(connection_details)
            with open("connection.json", "w+") as file:
                file.write(connection_json)
            rpc_connection = rpclib.rpc_connect(rpc_user, rpc_password, int(rpc_port))
            break
        else:
            print(colorize("Please input y or n", "red"))
    return rpc_connection


def getinfo_tui(rpc_connection):

    info_raw = rpclib.getinfo(rpc_connection)
    if isinstance(info_raw, dict):
        for key in info_raw:
            print("{}: {}".format(key, info_raw[key]))
        input("Press [Enter] to continue...")
    else:
        print("Error!\n")
        print(info_raw)
        input("\nPress [Enter] to continue...")


def token_create_tui(rpc_connection):

    while True:
        try:
            name = input("Set your token name: ")
            supply = input("Set your token supply: ")
            description = input("Set your token description: ")
        except KeyboardInterrupt:
            break
        else:
            token_hex = rpclib.token_create(rpc_connection, name, supply, description)
        if token_hex['result'] == "error":
            print(colorize("\nSomething went wrong!\n", "pink"))
            print(token_hex)
            print("\n")
            input("Press [Enter] to continue...")
            break
        else:
            try:
                token_txid = rpclib.sendrawtransaction(rpc_connection,
                                                       token_hex['hex'])
            except KeyError:
                print(token_txid)
                print("Error")
                input("Press [Enter] to continue...")
                break
            finally:
                print(colorize("Token creation transaction broadcasted: " + token_txid, "green"))
                file = open("tokens_list", "a")
                file.writelines(token_txid + "\n")
                file.close()
                print(colorize("Entry added to tokens_list file!\n", "green"))
                input("Press [Enter] to continue...")
                break


def oracle_create_tui(rpc_connection):

    print(colorize("\nAvailiable data types:\n", "blue"))
    oracles_data_types = ["Ihh -> height, blockhash, merkleroot\ns -> <256 char string\nS -> <65536 char string\nd -> <256 binary data\nD -> <65536 binary data",
                "c -> 1 byte signed little endian number, C unsigned\nt -> 2 byte signed little endian number, T unsigned",
                "i -> 4 byte signed little endian number, I unsigned\nl -> 8 byte signed little endian number, L unsigned",
                "h -> 32 byte hash\n"]
    for oracles_type in oracles_data_types:
        print(str(oracles_type))
    while True:
        try:
            name = input("Set your oracle name: ")
            description = input("Set your oracle description: ")
            oracle_data_type = input("Set your oracle type (e.g. Ihh): ")
        except KeyboardInterrupt:
            break
        else:
            oracle_hex = rpclib.oracles_create(rpc_connection, name, description, oracle_data_type)
        if oracle_hex['result'] == "error":
            print(colorize("\nSomething went wrong!\n", "pink"))
            print(oracle_hex)
            print("\n")
            input("Press [Enter] to continue...")
            break
        else:
            try:
                oracle_txid = rpclib.sendrawtransaction(rpc_connection, oracle_hex['hex'])
            except KeyError:
                print(oracle_txid)
                print("Error")
                input("Press [Enter] to continue...")
                break
            finally:
                print(colorize("Oracle creation transaction broadcasted: " + oracle_txid, "green"))
                file = open("oracles_list", "a")
                file.writelines(oracle_txid + "\n")
                file.close()
                print(colorize("Entry added to oracles_list file!\n", "green"))
                input("Press [Enter] to continue...")
                break


def oracle_register_tui(rpc_connection):
    #TODO: have an idea since blackjoker new RPC call
    #grab all list and printout only or which owner match with node pubkey
    try:
        print(colorize("Oracles created from this instance by TUI: \n", "blue"))
        with open("oracles_list", "r") as file:
            for oracle in file:
                print(oracle)
        print(colorize('_' * 65, "blue"))
        print("\n")
    except FileNotFoundError:
        print("Seems like a no oracles created from this instance yet\n")
        pass
    while True:
        try:
            oracle_id = input("Input txid of oracle you want to register to: ")
            data_fee = input("Set publisher datafee (in satoshis): ")
        except KeyboardInterrupt:
            break
        oracle_register_hex = rpclib.oracles_register(rpc_connection, oracle_id, data_fee)
        if oracle_register_hex['result'] == "error":
            print(colorize("\nSomething went wrong!\n", "pink"))
            print(oracle_register_hex)
            print("\n")
            input("Press [Enter] to continue...")
            break
        else:
            try:
                oracle_register_txid = rpclib.sendrawtransaction(rpc_connection, oracle_register_hex['hex'])
            except KeyError:
                print(oracle_register_hex)
                print("Error")
                input("Press [Enter] to continue...")
                break
            else:
                print(colorize("Oracle registration transaction broadcasted: " + oracle_register_txid, "green"))
                input("Press [Enter] to continue...")
                break


def oracle_subscription_utxogen(rpc_connection):
    # TODO: have an idea since blackjoker new RPC call
    # grab all list and printout only or which owner match with node pubkey
    try:
        print(colorize("Oracles created from this instance by TUI: \n", "blue"))
        with open("oracles_list", "r") as file:
            for oracle in file:
                print(oracle)
        print(colorize('_' * 65, "blue"))
        print("\n")
    except FileNotFoundError:
        print("Seems like a no oracles created from this instance yet\n")
        pass
    while True:
        try:
            oracle_id = input("Input oracle ID you want to subscribe to: ")
            #printout to fast copypaste publisher id
            oracle_info = rpclib.oracles_info(rpc_connection, oracle_id)
            publishers = 0
            print(colorize("\nPublishers registered for a selected oracle: \n", "blue"))
            try:
                for entry in oracle_info["registered"]:
                    publisher = entry["publisher"]
                    print(publisher + "\n")
                    publishers = publishers + 1
                print("Total publishers:{}".format(publishers))
            except (KeyError, ConnectionResetError):
                print(colorize("Please re-check your input. Oracle txid seems not valid.", "red"))
                pass
            print(colorize('_' * 65, "blue"))
            print("\n")
            if publishers == 0:
                print(colorize("This oracle have no publishers to subscribe.\n"
                               "Please register as an oracle publisher first and/or wait since registration transaciton mined!", "red"))
                input("Press [Enter] to continue...")
                break
            publisher_id = input("Input oracle publisher id you want to subscribe to: ")
            data_fee = input("Input subscription fee (in COINS!): ")
            utxo_num = int(input("Input how many transactions you want to broadcast: "))
        except KeyboardInterrupt:
            break
        while utxo_num > 0:
            while True:
                oracle_subscription_hex = rpclib.oracles_subscribe(rpc_connection, oracle_id, publisher_id, data_fee)
                oracle_subscription_txid = rpclib.sendrawtransaction(rpc_connection, oracle_subscription_hex['hex'])
                mempool = rpclib.get_rawmempool(rpc_connection)
                if oracle_subscription_txid in mempool:
                    break
                else:
                    pass
            print(colorize("Oracle subscription transaction broadcasted: " + oracle_subscription_txid, "green"))
            utxo_num = utxo_num - 1
        input("Press [Enter] to continue...")
        break


def token_converter_tui(rpc_connection):
    #TODO: have an idea since blackjoker new RPC call
    #grab all list and printout only or which owner match with node pubkey
    try:
        print(colorize("Tokens created from this instance by TUI: \n", "blue"))
        with open("tokens_list", "r") as file:
            for oracle in file:
                print(oracle)
        print(colorize('_' * 65, "blue"))
        print("\n")
    except FileNotFoundError:
        print("Seems like a no oracles created from this instance yet\n")
        pass
    while True:
        try:
            evalcode = "241"
            token_id = input("Input id of token which you want to convert: ")
            # informative printouts
            token_info = rpclib.token_info(rpc_connection, token_id)
            token_balance = rpclib.token_balance(rpc_connection, token_id)
            try:
                print(colorize("\n{} token supply: {}\n".format(token_id, token_info["supply"]), "blue"))
                print("Your pubkey balance for this token: {}\n".format(token_balance["balance"]))
            except (KeyError, ConnectionResetError):
                print(colorize("Please re-check your input", "red"))
                input("Press [Enter] to continue...")
                break
            print(colorize('_' * 65, "blue"))
            print("\n")
            pubkey = input("Input pubkey to which you want to convert (for initial conversion use \
03ea9c062b9652d8eff34879b504eda0717895d27597aaeb60347d65eed96ccb40): ")
            # TODO: have to print here pubkey with which started chain daemon
            supply = str(input("Input supply which you want to convert (for initial conversion set all token supply): "))
        except KeyboardInterrupt:
            break
        token_convert_hex = rpclib.token_convert(rpc_connection, evalcode, token_id, pubkey, supply)
        if token_convert_hex['result'] == "error":
            print(colorize("\nSomething went wrong!\n", "pink"))
            print(token_convert_hex)
            print("\n")
            input("Press [Enter] to continue...")
            break
        else:
            try:
                token_convert_txid = rpclib.sendrawtransaction(rpc_connection, token_convert_hex['hex'])
            except KeyError:
                print(token_convert_hex)
                print("Error")
                input("Press [Enter] to continue...")
                break
            else:
                print(colorize("Token convertion transaction broadcasted: " + token_convert_txid, "green"))
                file = open("token_convert_list", "a")
                file.writelines(token_convert_txid + "\n")
                file.close()
                print(colorize("Entry added to token_convert_list file!\n", "green"))
                input("Press [Enter] to continue...")
                break


def gateways_bind_tui(rpc_connection):
    # main loop with keyboard interrupt handling
    while True:
        try:
            while True:
                try:
                    print(colorize("Tokens created from this instance by TUI: \n", "blue"))
                    with open("tokens_list", "r") as file:
                        for oracle in file:
                            print(oracle)
                    print(colorize('_' * 65, "blue"))
                    print("\n")
                except FileNotFoundError:
                    print("Seems like a no oracles created from this instance yet\n")
                    pass
                token_id = input("Input id of token you want to use in gw bind: ")
                try:
                    token_name = rpclib.token_info(rpc_connection, token_id)["name"]
                except KeyError:
                    print(colorize("Not valid tokenid. Please try again.", "red"))
                    input("Press [Enter] to continue...")
                token_info = rpclib.token_info(rpc_connection, token_id)
                print(colorize("\n{} token total supply: {}\n".format(token_id, token_info["supply"]), "blue"))
                token_supply = input("Input supply for token binding: ")
                try:
                    print(colorize("\nOracles created from this instance by TUI: \n", "blue"))
                    with open("oracles_list", "r") as file:
                        for oracle in file:
                            print(oracle)
                    print(colorize('_' * 65, "blue"))
                    print("\n")
                except FileNotFoundError:
                    print("Seems like a no oracles created from this instance yet\n")
                    pass
                oracle_id = input("Input id of oracle you want to use in gw bind: ")
                try:
                    oracle_name = rpclib.oracles_info(rpc_connection, oracle_id)["name"]
                except KeyError:
                    print(colorize("Not valid oracleid. Please try again.", "red"))
                    input("Press [Enter] to continue...")
                while True:
                    coin_name = input("Input external coin ticker (binded oracle and token need to have same name!): ")
                    if token_name == oracle_name and token_name == coin_name:
                        break
                    else:
                        print(colorize("Token name, oracle name and external coin ticker should match!", "red"))
                while True:
                    M = input("Input minimal amount of pubkeys needed for transaction confirmation (1 for non-multisig gw): ")
                    N = input("Input maximal amount of pubkeys needed for transaction confirmation (1 for non-multisig gw): ")
                    if (int(N) >= int(M)):
                        break
                    else:
                        print("Maximal amount of pubkeys should be more or equal than minimal. Please try again.")
                pubkeys = []
                for i in range(int(N)):
                    pubkeys.append(input("Input pubkey {}: ".format(i+1)))
                #pubkeys = ', '.join(pubkeys)
                args = [rpc_connection, token_id, oracle_id, coin_name, token_supply, M, N]
                args = args + pubkeys
                # broadcasting block
                try:
                    gateways_bind_hex = rpclib.gateways_bind(*args)
                except Exception as e:
                    print(e)
                    input("Press [Enter] to continue...")
                    break
                try:
                    gateways_bind_txid = rpclib.sendrawtransaction(rpc_connection, gateways_bind_hex["hex"])
                except Exception as e:
                    print(e)
                    print(gateways_bind_hex)
                    input("Press [Enter] to continue...")
                    break
                else:
                    print(colorize("Gateway bind transaction broadcasted: " + gateways_bind_txid, "green"))
                    file = open("gateways_list", "a")
                    file.writelines(gateways_bind_txid + "\n")
                    file.close()
                    print(colorize("Entry added to gateways_list file!\n", "green"))
                    input("Press [Enter] to continue...")
                    break
            break
        except KeyboardInterrupt:
            break

# temporary :trollface: custom connection function solution
# to have connection to KMD daemon and cache it in separate file


def rpc_kmd_connection_tui():
    while True:
        restore_choice = input("Do you want to use KMD daemon connection details from previous session? [y/n]: ")
        if restore_choice == "y":
            try:
                with open("connection_kmd.json", "r") as file:
                    connection_json = json.load(file)
                    rpc_user = connection_json["rpc_user"]
                    rpc_password = connection_json["rpc_password"]
                    rpc_port = connection_json["rpc_port"]
                    rpc_connection_kmd = rpclib.rpc_connect(rpc_user, rpc_password, int(rpc_port))
                    try:
                        print(rpc_connection_kmd.getinfo())
                        print(colorize("Successfully connected!\n", "green"))
                        input("Press [Enter] to continue...")
                        break
                    except Exception as e:
                        print(e)
                        print(colorize("NOT CONNECTED!\n", "red"))
                        input("Press [Enter] to continue...")
                        break
            except FileNotFoundError:
                print(colorize("You do not have cached KMD daemon connection details."
                               " Please select n for connection setup", "red"))
                input("Press [Enter] to continue...")
        elif restore_choice == "n":
            rpc_user = input("Input your rpc user: ")
            rpc_password = input("Input your rpc password: ")
            rpc_port = input("Input your rpc port: ")
            connection_details = {"rpc_user": rpc_user,
                                  "rpc_password": rpc_password,
                                  "rpc_port": rpc_port}
            connection_json = json.dumps(connection_details)
            with open("connection_kmd.json", "w+") as file:
                file.write(connection_json)
            rpc_connection_kmd = rpclib.rpc_connect(rpc_user, rpc_password, int(rpc_port))
            try:
                print(rpc_connection_kmd.getinfo())
                print(colorize("Successfully connected!\n", "green"))
                input("Press [Enter] to continue...")
                break
            except Exception as e:
                print(e)
                print(colorize("NOT CONNECTED!\n", "red"))
                input("Press [Enter] to continue...")
                break
        else:
            print(colorize("Please input y or n", "red"))
    return rpc_connection_kmd


def z_sendmany_twoaddresses(rpc_connection, sendaddress, recepient1, amount1, recepient2, amount2):
    str_sending_block = "[{{\"address\":\"{}\",\"amount\":{}}},{{\"address\":\"{}\",\"amount\":{}}}]".format(recepient1, amount1, recepient2, amount2)
    sending_block = json.loads(str_sending_block)
    operation_id = rpc_connection.z_sendmany(sendaddress,sending_block)
    return operation_id


def operationstatus_to_txid(rpc_connection, zstatus):
    str_sending_block = "[\"{}\"]".format(zstatus)
    sending_block = json.loads(str_sending_block)
    operation_json = rpc_connection.z_getoperationstatus(sending_block)
    operation_dump = json.dumps(operation_json)
    operation_dict = json.loads(operation_dump)[0]
    txid = operation_dict['result']['txid']
    return txid


def gateways_send_kmd(rpc_connection):
     # TODO: have to handle CTRL+C on text input
     print(colorize("Please be carefull when input wallet addresses and amounts since all transactions doing in real KMD!", "pink"))
     print("Your addresses with balances: ")
     list_address_groupings = rpc_connection.listaddressgroupings()
     for address in list_address_groupings:
         print(str(address) + "\n")
     sendaddress = input("Input address from which you transfer KMD: ")
     recepient1 = input("Input address which belongs to pubkey which will receive tokens: ")
     amount1 = 0.0001
     recepient2 = input("Input gateway deposit address: ")
     file = open("deposits_list", "a")
     #have to show here deposit addresses for gateways created by user
     amount2 = input("Input how many KMD you want to deposit on this gateway: ")
     operation = z_sendmany_twoaddresses(rpc_connection, sendaddress, recepient1, amount1, recepient2, amount2)
     print("Operation proceed! " + str(operation) + " Let's wait 2 seconds to get txid")
     # trying to avoid pending status of operation
     time.sleep(2)
     txid = operationstatus_to_txid(rpc_connection, operation)
     file.writelines(txid + "\n")
     file.close()
     print(colorize("KMD Transaction ID: " + str(txid) + " Entry added to deposits_list file", "green"))
     input("Press [Enter] to continue...")


def gateways_deposit_tui(rpc_connection_kmd, rpc_connection):
    while True:
        bind_txid = input("Input your gateway bind txid: ")
        coin_name = input("Input your external coin ticker (e.g. KMD): ")
        coin_txid = input("Input your deposit txid: ")
        dest_pub = input("Input pubkey which claim deposit: ")
        amount = input("Input amount of your deposit: ")
        height = rpc_connection_kmd.getrawtransaction(coin_txid, 1)["height"]
        # print("height=" + str(height) + "\n")
        deposit_kmd_hex = rpc_connection_kmd.getrawtransaction(coin_txid, 1)["hex"]
        # print("coin_tx=" + deposit_kmd_hex + "\n")
        claim_vout = "0"
        proof_sending_block = "[\"{}\"]".format(coin_txid)
        proof = rpc_connection_kmd.gettxoutproof(json.loads(proof_sending_block))
        # print("proof " + str(proof) + "\n")
        deposit_hex = rpclib.gateways_deposit(rpc_connection, bind_txid, str(height), coin_name, \
                         coin_txid, claim_vout, deposit_kmd_hex, proof, dest_pub, amount)
        print("deposit_hex=" + str(deposit_hex) + "\n")
        deposit_txid = rpclib.sendrawtransaction(rpc_connection, deposit_hex["hex"])
        print(deposit_txid)
        input("Press [Enter] to continue...")
        break


def gateways_claim_tui(rpc_connection):
    while True:
        bind_txid = input("Input your gateway bind txid: ")
        coin_name = input("Input your external coin ticker (e.g. KMD): ")
        deposit_txid = input("Input your gatewaysdeposit txid: ")
        dest_pub = input("Input pubkey which claim deposit: ")
        amount = input("Input amount of your deposit: ")
        claim_hex = rpclib.gateways_claim(rpc_connection, bind_txid, coin_name, deposit_txid, dest_pub, amount)
        claim_txid = rpclib.sendrawtransaction(rpc_connection, claim_hex["hex"])
        print(claim_txid)
        input("Press [Enter] to continue...")
        break


def gateways_withdrawal_tui(rpc_connection):
    while True:
        bind_txid = input("Input your gateway bind txid: ")
        coin_name = input("Input your external coin ticker (e.g. KMD): ")
        withdraw_pub = input("Input pubkey to which you want to withdraw: ")
        amount = input("Input amount of withdrawal: ")
        withdraw_hex = rpclib.gateways_withdraw(rpc_connection, bind_txid, coin_name, withdraw_pub, amount)
        withdraw_txid = rpclib.sendrawtransaction(rpc_connection, withdraw_hex["hex"])
        print(withdraw_txid)
        input("Press [Enter] to continue...")
        break
