import re

import MySQLdb


class DocumentNotFound(Exception):
    pass


class WordPressReader(object):
    def __init__(
            self,
            host,
            user,
            passwd,
            db,
            internal_cms_link_prefix,
            content_path_prefix,
            port=3306,
            connect_timeout=30,
            table_prefix='wp'):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.db = db
        self.connect_timeout = connect_timeout
        self.table_prefix = table_prefix
        self.internal_cms_link_prefix = internal_cms_link_prefix
        self.content_path_prefix = content_path_prefix
        self._connection = None

    def _connect(self):
        self._connection = MySQLdb.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            passwd=self.passwd,
            connect_timeout=self.connect_timeout,
            db=self.db,
            use_unicode=True,
            charset='utf8',
        )

    @property
    def connection(self):
        if not self._connection:
            self._connect()
        return self._connection

    def query(self, *args):
        try:
            cursor = self.connection.cursor()
            cursor.execute(*args)
        except (AttributeError, MySQLdb.OperationalError):
            self._connect()
            cursor = self.connection.cursor()
            cursor.execute(*args)
        self.connection.commit()
        return cursor

    def get_descendants_for_id(self, wp_id):
        sql = """
            SELECT
                parent.id AS parent_id,
                parent.post_title AS parent_title,
                child.post_title AS child_title,
                child.post_name AS child_slug
            FROM
                {0}_posts AS parent
                inner join {0}_posts AS child ON parent.ID = child.post_parent
                inner join {0}_posts AS super ON super.ID = parent.post_parent
            WHERE
                parent.post_parent = %s
                AND super.post_status = 'publish'
                AND parent.post_status = 'publish'
                AND child.post_status = 'publish'
            ORDER BY
                parent.menu_order,
                child.menu_order
            """.format(self.table_prefix)
        cursor = self.query(sql, (wp_id,))
        results = []
        last_parent_id = None
        for row in cursor:
            if last_parent_id != row[0]:
                parent_document = WordPressParent(
                    title=row[1],
                    children=[{'title': row[2], 'slug': row[3]}])
                results.append(parent_document)
            else:
                results[-1].children.append(
                    {'title': row[2], 'slug': row[3]})
            last_parent_id = row[0]

        return results

    def get_document_by_slug(self, wp_slug):
        return WordPressDocument.from_wp_slug(
            self,
            self.table_prefix,
            self.internal_cms_link_prefix,
            self.content_path_prefix,
            wp_slug)

    def get_parent_by_id(self, wp_id):
        return WordPressParent.from_wp_id(self, self.table_prefix, wp_id)


class WordPressDocument(object):
    def __init__(
            self,
            internal_cms_link_prefix,
            content_path_prefix,
            title,
            content):
        self._internal_cms_link_prefix = internal_cms_link_prefix
        self._content_path_prefix = content_path_prefix
        self.title = title
        self._content = content

    @property
    def content(self):
        return re.sub(
            r'href="{0}([a-z0-9/-]+)?/(?P<post_name>[^/]+)/"'.format(
                self._internal_cms_link_prefix),
            r'href="{0}\g<post_name>/"'.format(self._content_path_prefix),
            self._content)

    @classmethod
    def from_wp_slug(
            cls,
            reader,
            table_prefix,
            internal_cms_link_prefix,
            content_path_prefix,
            wp_slug):
        sql = """
            SELECT post_title AS title, post_content AS content
            FROM %s_posts
            WHERE post_name = %%s
            """ % (table_prefix)
        cursor = reader.query(sql, (wp_slug,))
        record = cursor.fetchone()
        if not record:
            raise DocumentNotFound(
                'WordPressDocument.from_wp_slug(%s) does not exist' % (wp_slug)
            )
        title = record[0]
        content = record[1]

        return cls(
            internal_cms_link_prefix,
            content_path_prefix,
            title,
            content)


class WordPressParent(object):

    def __init__(self, title, children):
        self.title = title
        self.children = children

    @classmethod
    def from_wp_id(cls, reader, table_prefix, wp_id):
        parent_sql = """
            SELECT post_title AS title
            FROM %s_posts
            WHERE ID = %%s
            AND post_status = 'publish'
            """ % (table_prefix)
        cursor = reader.query(parent_sql, (wp_id,))
        parent_record = cursor.fetchone()
        if not parent_record:
            raise DocumentNotFound(
                'WordPressParent.from_wp_id(%s) does not exist '
                'or is not published' % (wp_id))
        title = parent_record[0]

        children_sql = """
            SELECT post_title AS title, post_name AS slug
            FROM %s_posts
            WHERE post_parent = %%s
            AND post_status = 'publish'
            ORDER BY menu_order
            """ % (table_prefix)
        cursor = reader.query(children_sql, (wp_id,))
        children = []
        if cursor.rowcount > 0:
            child_records = []
            columns = tuple(
                [d[0].decode('utf8') for d in cursor.description])
            for row in cursor:
                child_records.append(dict(zip(columns, row)))
            children = child_records

        return cls(title, children)
