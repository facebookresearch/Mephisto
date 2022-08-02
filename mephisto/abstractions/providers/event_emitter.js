class EventEmitter {
  subscriptions = new Map();

  subscribe(eventName, callback) {
    if (!this.subscriptions.has(eventName)) {
      this.subscriptions.set(eventName, new Set());
    }
    const subscriptions = this.subscriptions.get(eventName);
    const callbackObj = { callback };
    subscriptions.add(callbackObj);

    return {
      release: () => {
        subscriptions.delete(callbackObj);
        if (subscriptions.size === 0) {
          delete this.subscriptions.eventName;
        }
      },
    };
  }

  emit(eventName, ...args) {
    const subscriptions = this.subscriptions.get(eventName);
    if (subscriptions) {
      subscriptions.forEach((cbObj) => {
        cbObj.callback.apply(this, args);
      });
    }
  }
}

export const emitter = new EventEmitter();
