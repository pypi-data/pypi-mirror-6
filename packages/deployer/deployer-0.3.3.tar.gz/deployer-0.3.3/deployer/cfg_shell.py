




run git.checkout('commit')

git[<all>].checkout(<commit>)


django[<all>].uwsgi[<all>].reload()



cp <from> <to>
cp my-file.py


class CopyNode:
    grammar = [
            Literal("cp"),
            FileCompleter(),
            FileCompleter(), ]

    def handler(self):
        pass

