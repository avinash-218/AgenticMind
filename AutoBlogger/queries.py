ME_QUERY = """
    query Me {
      me {
        id
        username
        name
        bio {
          text
        }
        profilePicture
        socialMediaLinks {
          website
          github
          twitter
          linkedin
        }
        followersCount
        followingsCount
        tagline
        location
        dateJoined
        role
        publications(first: 5) {
          edges {
            node {
              id
              title
              # remove 'domain' because it's not on Publication
              # if you want url-like info, you may need other fields here
            }
          }
          totalDocuments
        }
        techStack(page: 1, pageSize: 20) {
          nodes {
            name
            slug
          }
          totalDocuments
        }
      }
    }
    """

CREATE_DRAFT_QUERY = """
    mutation CreateDraft($input: CreateDraftInput!) {
      createDraft(input: $input) {
        draft {
          id
          title
          slug
          subtitle
          readTimeInMinutes
          dateUpdated
          updatedAt
          canonicalUrl
          isSubmittedForReview
          publication {
            id
            title
          }
          author {
            name
            username
          }
          tags {
            name
            slug
          }
        }
      }
    }
    """

GET_PUBLICATION_QUERY = """
    query GetPublication {
      me {
        publications(first: 1) {
          edges {
            node {
              id
              title
            }
          }
        }
      }
    }
    """

PUBLISH_DRAFT_QUERY = """
    mutation PublishDraft($input: PublishDraftInput!) {
      publishDraft(input: $input) {
        post {
          id
          title
          slug
          subtitle
          url
          canonicalUrl
          brief
          readTimeInMinutes
          publishedAt
          updatedAt
          views
          reactionCount
          replyCount
          responseCount
          featured
          tags {
            name
            slug
          }
          publication {
            id
            title
          }
          author {
            name
            username
          }
        }
      }
    }
    """

UPDATE_POST_QUERY = """
mutation UpdatePost($input: UpdatePostInput!) {
  updatePost(input: $input) {
    post {
      id
      title
      slug
      updatedAt
      url
      tags {
        name
        slug
      }
      publication {
        title
      }
      author {
        name
        username
      }
    }
  }
}
"""

REMOVE_POST_QUERY = """
mutation RemovePost($input: RemovePostInput!) {
  removePost(input: $input) {
    post {
      id
      title
      slug
      publication {
        title
      }
      author {
        name
        username
      }
      updatedAt
      publishedAt
    }
  }
}
"""

PUBLICATION_QUERY = """
    query Publication($host: String!) {
      publication(host: $host) {
        isTeam
        title
        about {
          markdown
        }
      }
    }
    """

PUBLICATION_POSTS_QUERY = """
query Publication($host: String!, $limit: Int!) {
  publication(host: $host) {
    isTeam
    title
    posts(first: $limit) {
      edges {
        node {
          title
          brief
          url
        }
      }
    }
  }
}
"""
