from pathlib import Path

cwd = Path.cwd()

print(cwd)

mod_path = Path(__file__).parent

print(mod_path)

relative_path_1 = 'same/parent/with/helper/script/'
relative_path_2 = '../../../or/any/level/up/'
src_path_1 = (mod_path / relative_path_1).resolve()
src_path_2 = (mod_path / relative_path_2).resolve()

##print(src_path_1)

##print(src_path_2)