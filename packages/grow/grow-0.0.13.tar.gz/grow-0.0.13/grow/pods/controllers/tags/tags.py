from grow.pods.collectionz import collectionz
import markdown
import itertools



def categories(collection=None, collections=None, reverse=None, order_by=None, _pod=None):
  if isinstance(collection, collectionz.Collection):
    collection = collection
  elif isinstance(collection, basestring):
    collection = _pod.get_collection(collection)
  else:
    text = '{} must be a Collection instance or a collection path, found: {}.'
    raise ValueError(text.format(collection, type(collection)))

  category_list = collection.list_categories()
  def order_func(doc):
    return category_list.index(doc.category)

  docs = [doc for doc in collection.list_documents(reverse=reverse, order_by='order')]
  docs = sorted(docs, key=order_func)
  items = itertools.groupby(docs, key=order_func)
  return ((category_list[index], pages) for index, pages in items)


def docs(collection, locale=None, order_by=None, _pod=None):
  collection = _pod.get_collection(collection)
  return collection.search_docs(locale=locale, order_by=order_by)


def is_active(active_doc, this_doc):
  return this_doc == active_doc


def markdown_filter(value):
  return markdown.markdown(value.decode('utf-8'))


def static(path, _pod=None):
  # TODO(jeremydw): Implement this.
  return path


def get_doc(pod_path, locale=None, _pod=None):
  return _pod.get_doc(pod_path, locale=locale)


def nav(collection, locale, _pod):
  colection = _pod.get_collection(collection)
