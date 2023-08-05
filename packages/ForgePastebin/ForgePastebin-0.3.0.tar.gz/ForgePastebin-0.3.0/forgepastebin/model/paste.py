from ming import schema as S
from ming.orm import FieldProperty, Mapper
from ming.utils import LazyProperty

from allura import model as M

class Paste(M.Artifact):
    class __mongometa__:
        name='paste'
        #indexes = [ ]
    type_s='Paste'

    creator_id = FieldProperty(S.ObjectId, required=True)
    text = FieldProperty(str, if_missing='')
    lang = FieldProperty(str, if_missing='')
    private = FieldProperty(bool, if_missing=False)

    @LazyProperty
    def creator(self):
        return M.User.query.get(_id=self.creator_id)

    def html(self, linenos=True):
        from pygments import highlight
        from pygments.lexers import get_lexer_by_name, guess_lexer
        from pygments.formatters import HtmlFormatter
        if self.lang:
            lexer = get_lexer_by_name(self.lang, stripall=True)
        else:
            lexer = guess_lexer(self.text)
        formatter = HtmlFormatter(linenos=linenos, cssclass="highlight")
        return highlight(self.text, lexer, formatter)

    def index(self):
        result = super(Paste, self).index()
        result.update(
            creator_id_s=self.creator_id,
            creator_s=self.creator.username,
            text=self.text,
            is_private_b=self.private,)
        return result

    def index_id(self):
        return 'Paste:%s' % self._id

    @property
    def lines(self):
        return len(self.text.split('\n'))

    def shorthand_id(self):
        return str(self._id) # pragma no cover

    def snippet(self, lines=5):
        return '\n'.join(self.text.split('\n')[:lines])

    def url(self):
        return (self.app_config.url() + str(self._id))

Mapper.compile_all()
