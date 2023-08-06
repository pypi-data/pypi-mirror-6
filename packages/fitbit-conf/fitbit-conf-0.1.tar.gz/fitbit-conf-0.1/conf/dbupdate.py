import os
import datetime
from .common import dinput, Config


def main():
    config = Config('/site/conf/server_apps/mysql/{0}/')
    update_path_template = config.dir()
    script_dict = {"r": "Updates", "f": "Future"}
    sql_files_dict = {
        "s": "updateShard.sql",
        "n": "updateUnifiedDb.sql",
        "f": "updateFood.sql",
        "rs": "rollbackShard.sql",
        "rn": "rollbackUnifiedDb.sql",
        "i": "updateInfrastructureDb.sql"
    }
    folder_postfix_dict = {
        "default": "",
        "pre": "PreRelease",
        "post": "PostRelease",
    }
    script_type_suffix = script_dict[dinput("Is it future (f) or regular (r) update?", "r")]
    suffixes = dict(
        (line.split(":")[0].rstrip(), line.split(":")[1].rstrip()) for line in open(
            update_path_template.format(script_dict['r']) + 'env_suffixes'))
    suffix_mappings = dict((n, suffix) for n, suffix in enumerate(suffixes.keys()))
    sql_file_input = input(
        "What files do you want to create? (Enter as comma separated values, e.g. s,rs)\n{0}:".format(sql_files_dict))
    sql_folder = datetime.date.today().strftime("%Y%m%d") + "-" + input("Script name:")
    env_suffix = ""
    if dinput("Is your script environment specific? (y/n):", 'n') == 'y':
        print("Possible prefixes are:\n{0}".format("\n".join(k + ":" + suffixes[k] for k in suffixes)))
        print(suffix_mappings)
        env_suffix = "-" + suffix_mappings[int(input("Enter number of the suffix:"))]
    file_names = [sql_files_dict[db.strip()] for db in sql_file_input.split(",")]
    sql_folder += env_suffix
    folder_postfix = folder_postfix_dict[dinput("{0} ?".format(folder_postfix_dict), 'default')]
    if folder_postfix: folder_postfix = '-' + folder_postfix
    sql_folder += folder_postfix
    folder_path = update_path_template.format(script_type_suffix) + sql_folder
    print("Following files will be create in '{0}' : {1}".format(folder_path, ",".join(file_names)))
    if input("Continue? (y/n):") == 'y':
        os.makedirs(folder_path)
        for file_name in file_names:
            open(folder_path + "/" + file_name, 'w')