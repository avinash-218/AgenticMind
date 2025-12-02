
# ---------------------------
# ✅ GraphQL Queries
# ---------------------------

TEST_QUERY = """
query {
  me {
    id
    username
  }
}
"""

GET_PUBLICATION_ID_QUERY = """
query GetPublications {
  me {
    publications(first: 1) {
      edges {
        node {
          id
          title
          domain
        }
      }
    }
  }
}
"""

CREATE_ARTICLE_MUTATION = """
mutation CreateDraft($input: CreateDraftInput!) {
  createDraft(input: $input) {
    draft {
      id
      title
      slug
    }
  }
}
"""

PUBLISH_ARTICLE_MUTATION = """
mutation PublishPost($draftId: ID!) {
  publishPost(draftId: $draftId) {
    post {
      id
      title
      slug
      url
    }
  }
}
"""

UPDATE_ARTICLE_MUTATION = """
mutation UpdatePost($input: UpdatePostInput!) {
  updatePost(input: $input) {
    post {
      id
      title
      slug
      url
    }
  }
}
"""

SEARCH_POSTS_OF_PUBLICATION_QUERY = """
query SearchPostsOfPublication($first: Int!, $filter: SearchPostsOfPublicationFilter) {
  searchPostsOfPublication(first: $first, filter: $filter) {
    edges {
      node {
        id
        title
        slug
        brief
        publishedAt
        author { name }
      }
    }
  }
}
"""

GET_POST_BY_ID_QUERY = """
query GetPostById($id: ID!) {
  post(id: $id) {
    id
    title
    contentMarkdown
    brief
    slug
    url
    publishedAt
    author { name }
  }
}
"""

GET_USER_INFO_QUERY = """
query GetUserInfo($username: String!) {
  user(username: $username) {
    id
    name
    username
    tagline
    publicationDomain
  }
}
"""

GET_TOP_ARTICLES_QUERY = """
query GetTopArticles {
  topStoriesFeed {
    edges {
      node {
        id
        title
        slug
        url
      }
    }
  }
}
"""

GET_ARTICLES_BY_TAG_QUERY = """
query GetArticlesByTag($tagSlug: String!) {
  tag(slug: $tagSlug) {
    posts(first: 5) {
      edges {
        node {
          id
          title
          slug
          url
        }
      }
    }
  }
}
"""