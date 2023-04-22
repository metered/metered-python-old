### `login`

```python
import httpimport

with httpimport.github_repo('metered', 'metered-python', ref='main'):
  import metered
  metered.auth.login()

  client = metered.client("text-embedding-all-minilm-l6-v2.metered.app")

```

### `request`

```python
import httpimport

with httpimport.github_repo('metered', 'metered-python', ref='main'):
  import metered

  client = metered.client("text-embedding-all-minilm-l6-v2.metered.app")

client.request(
    query='''query Q($texts: [String!]!) {
      embed(
        texts: $texts,
      ) {
        elements {
          embedding
        }
      }
    }
    ''',
    variables={"texts": ["hi"]},
)
```
