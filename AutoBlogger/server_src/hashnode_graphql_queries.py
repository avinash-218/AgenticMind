# Fetches the authenticated user's profile details, social links, tech stack,
# and a limited set of their publications
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

# Creates a new draft post under the authenticated user or a publication
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

# Retrieves the first publication associated with the authenticated user
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

# Publishes an existing draft and returns full post metadata after publishing
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

# Updates an existing published post or draft with new content or metadata
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

# Removes (unpublishes/deletes) a post and returns basic post information
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

# Fetches basic publication details using the publication host
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

# Retrieves a limited list of posts from a publication using the publication host
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
