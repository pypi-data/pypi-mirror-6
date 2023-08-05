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
            table_prefix,
            internal_cms_link_prefix,
            content_path_prefix):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db
        self.table_prefix = table_prefix
        self.internal_cms_link_prefix = internal_cms_link_prefix
        self.content_path_prefix = content_path_prefix
        self._connection = None

    @property
    def connection(self):
        if not self._connection:
            self._connection = MySQLdb.connect(
                host=self.host,
                user=self.user,
                passwd=self.passwd,
                db=self.db)
        return self._connection

    def get_document_by_slug(self, wp_slug):
        return WordPressDocument.from_wp_slug(
            self.connection,
            self.table_prefix,
            self.internal_cms_link_prefix,
            self.content_path_prefix,
            wp_slug)

    def get_parent_by_id(self, wp_id):
        return WordPressParent.from_wp_id(
            self.connection,
            self.table_prefix,
            wp_id)


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
            connection,
            table_prefix,
            internal_cms_link_prefix,
            content_path_prefix,
            wp_slug):
        cursor = connection.cursor()

        query = """
            SELECT post_title AS title, post_content AS content
            FROM %s_posts
            WHERE post_name = %%s
            """ % (table_prefix)
        cursor.execute(query, (wp_slug,))
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
    def from_wp_id(cls, connection, table_prefix, wp_id):
        cursor = connection.cursor()

        parent_query = """
            SELECT post_title AS title
            FROM %s_posts
            WHERE ID = %%s
            AND post_status = 'publish'
            """ % (table_prefix)
        cursor.execute(parent_query, (wp_id,))
        parent_record = cursor.fetchone()
        if not parent_record:
            raise DocumentNotFound(
                'WordPressParent.from_wp_id(%s) does not exist '
                'or is not published' % (wp_id))
        title = parent_record[0]

        children_query = """
            SELECT post_title AS title, post_name AS slug
            FROM %s_posts
            WHERE post_parent = %%s
            AND post_status = 'publish'
            ORDER BY menu_order
            """ % (table_prefix)
        cursor.execute(children_query, (wp_id,))
        children = []
        if cursor.rowcount > 0:
            child_records = []
            columns = tuple(
                [d[0].decode('utf8') for d in cursor.description])
            for row in cursor:
                child_records.append(dict(zip(columns, row)))
            children = child_records

        return cls(title, children)
