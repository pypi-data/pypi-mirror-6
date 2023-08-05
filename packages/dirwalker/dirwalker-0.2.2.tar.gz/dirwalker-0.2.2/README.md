# dirwalker

dirwalker is a Python package that walks multiple-level directories
searching for files with the given extensions.

## Requirements

* Python standard `os` module

## Usage

```python
import dirwalker
# Search with recursing subdirectories
dirwalker.find_filenames_with_extensions(
    '/Users/me/dev/search_directory',
    ['txt', '.csv'])
# Search without recursing subdirectories
dirwalker.find_filenames_with_extensions(
    '/Users/me/dev/search_directory',
    ['txt', '.csv'],
    recurse=False)
```

## Contributing

[dirwalker] is developed using [git-flow], which are "git extensions to
provide high-level repository operations for [Vincent Driessen's
branching model][nvie-git]." To contirbute, [install git-flow], fork
[dirwalker], and then run:

```bash
$ git clone git@github.com:<username>/dirwalker.git
$ cd dirwalker
$ git branch master origin/master
$ git flow init -d
$ git flow feature start <your_feature>
```

When you're done coding and committing the changes for `your_feature`,
issue:

```bash
$ git flow feature publish <your_feature>
```

Then open a pull request to `your_feature` branch.


# License

[dirwalker] is released under the MIT license. Please see the
[LICENSE.txt] file for more information.

[dirwalker]: https://github.com/matthewrankin/dirwalker
[numpy]: http://www.numpy.org
[siganalysis]: https://github.com/questrail/siganalysis
[git workflow]: http://nvie.com/posts/a-successful-git-branching-model/
[LICENSE.txt]: https://github.com/matthewrankin/dirwalker/blob/develop/LICENSE.txt
[git-flow]: https://github.com/nvie/gitflow
[nvie-git]: http://nvie.com/posts/a-successful-git-branching-model/
[install git-flow]: https://github.com/nvie/gitflow/wiki/Installation
