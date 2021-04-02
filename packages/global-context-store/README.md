# global-context-store

This package makes managing global state easier.

### Usage

First wrap your app with the `<Store />` context provider.

```jsx
import Store from "global-context-store";

// ...
return (
  <Store>
    <App />
  </Store>
)
```

Then, any descendent of `<Store />` can set and retrieve items from the global state via the `useStore` hook:

```jsx
import { useStore } from "global-context-store";

function DeepChildComponent() {
    const { set } = useStore()

    set("portfolio.stocks[0]", "AAPL")
}
```

This will update the state so it looks like:

```jsx
const { state } = useStore()
console.log(state)

// { portfolio: stocks: [ "AAPL" ]}
```

> `set(path, value)` uses `lodash.set` under-the-hood. Hence if a portion of the `path` doesn't exist, it's created. You can read up more on how it works here: https://lodash.com/docs/4.17.15#set

We also provide `get(path)`, `invoke(path, fn)`, `push(path, value)`, and `unset(path)`.

```jsx
const { set, get, invoke, push, unset } = useStore()

set("portfolio.stocks[0]", "AAPL")
get("portfolio") // { stocks: [ "AAPL"] }
get("portfolio.stocks") // [ "AAPL" ]

push("portfolio.stocks", "TSLA")
get("portfolio.stocks") // [ "AAPL", "TSLA" ]

invoke("portfolio.stocks", tickers => ticker.map(ticker => "$" + ticker) )
get("portfolio.stocks") // [ "$AAPL", "$TSLA" ]

unset("portfolio.stocks")
get("portfolio") // { }
```