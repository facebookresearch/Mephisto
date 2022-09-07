/*! For license information please see index.js.LICENSE.txt */
!(function (e, t) {
  "object" == typeof exports && "object" == typeof module
    ? (module.exports = t(require("react")))
    : "function" == typeof define && define.amd
    ? define(["react"], t)
    : "object" == typeof exports
    ? (exports["mephisto-worker-addons"] = t(require("react")))
    : (e["mephisto-worker-addons"] = t(e.react));
})(self, (e) =>
  (() => {
    var t = {
        659: (e, t, n) => {
          var r, o, i, a;
          function l(e) {
            return (
              (l =
                "function" == typeof Symbol &&
                "symbol" == typeof Symbol.iterator
                  ? function (e) {
                      return typeof e;
                    }
                  : function (e) {
                      return e &&
                        "function" == typeof Symbol &&
                        e.constructor === Symbol &&
                        e !== Symbol.prototype
                        ? "symbol"
                        : typeof e;
                    }),
              l(e)
            );
          }
          (e = n.nmd(e)),
            self,
            (a = function (e) {
              return (function () {
                var t = {
                    285: function (e, t, n) {
                      e.exports = n(490);
                    },
                    109: function (e, t, n) {
                      "use strict";
                      var r = n(702),
                        o = n(24),
                        i = n(140),
                        a = n(996),
                        l = n(922),
                        s = n(254),
                        u = n(823),
                        c = n(983);
                      e.exports = function (e) {
                        return new Promise(function (t, n) {
                          var f = e.data,
                            d = e.headers,
                            p = e.responseType;
                          r.isFormData(f) && delete d["Content-Type"];
                          var m = new XMLHttpRequest();
                          if (e.auth) {
                            var h = e.auth.username || "",
                              b = e.auth.password
                                ? unescape(encodeURIComponent(e.auth.password))
                                : "";
                            d.Authorization = "Basic " + btoa(h + ":" + b);
                          }
                          var g = l(e.baseURL, e.url);
                          function v() {
                            if (m) {
                              var r =
                                  "getAllResponseHeaders" in m
                                    ? s(m.getAllResponseHeaders())
                                    : null,
                                i = {
                                  data:
                                    p && "text" !== p && "json" !== p
                                      ? m.response
                                      : m.responseText,
                                  status: m.status,
                                  statusText: m.statusText,
                                  headers: r,
                                  config: e,
                                  request: m,
                                };
                              o(t, n, i), (m = null);
                            }
                          }
                          if (
                            (m.open(
                              e.method.toUpperCase(),
                              a(g, e.params, e.paramsSerializer),
                              !0
                            ),
                            (m.timeout = e.timeout),
                            "onloadend" in m
                              ? (m.onloadend = v)
                              : (m.onreadystatechange = function () {
                                  m &&
                                    4 === m.readyState &&
                                    (0 !== m.status ||
                                      (m.responseURL &&
                                        0 ===
                                          m.responseURL.indexOf("file:"))) &&
                                    setTimeout(v);
                                }),
                            (m.onabort = function () {
                              m &&
                                (n(c("Request aborted", e, "ECONNABORTED", m)),
                                (m = null));
                            }),
                            (m.onerror = function () {
                              n(c("Network Error", e, null, m)), (m = null);
                            }),
                            (m.ontimeout = function () {
                              var t = "timeout of " + e.timeout + "ms exceeded";
                              e.timeoutErrorMessage &&
                                (t = e.timeoutErrorMessage),
                                n(
                                  c(
                                    t,
                                    e,
                                    e.transitional &&
                                      e.transitional.clarifyTimeoutError
                                      ? "ETIMEDOUT"
                                      : "ECONNABORTED",
                                    m
                                  )
                                ),
                                (m = null);
                            }),
                            r.isStandardBrowserEnv())
                          ) {
                            var y =
                              (e.withCredentials || u(g)) && e.xsrfCookieName
                                ? i.read(e.xsrfCookieName)
                                : void 0;
                            y && (d[e.xsrfHeaderName] = y);
                          }
                          "setRequestHeader" in m &&
                            r.forEach(d, function (e, t) {
                              void 0 === f && "content-type" === t.toLowerCase()
                                ? delete d[t]
                                : m.setRequestHeader(t, e);
                            }),
                            r.isUndefined(e.withCredentials) ||
                              (m.withCredentials = !!e.withCredentials),
                            p &&
                              "json" !== p &&
                              (m.responseType = e.responseType),
                            "function" == typeof e.onDownloadProgress &&
                              m.addEventListener(
                                "progress",
                                e.onDownloadProgress
                              ),
                            "function" == typeof e.onUploadProgress &&
                              m.upload &&
                              m.upload.addEventListener(
                                "progress",
                                e.onUploadProgress
                              ),
                            e.cancelToken &&
                              e.cancelToken.promise.then(function (e) {
                                m && (m.abort(), n(e), (m = null));
                              }),
                            f || (f = null),
                            m.send(f);
                        });
                      };
                    },
                    490: function (e, t, n) {
                      "use strict";
                      var r = n(702),
                        o = n(882),
                        i = n(595),
                        a = n(12);
                      function l(e) {
                        var t = new i(e),
                          n = o(i.prototype.request, t);
                        return r.extend(n, i.prototype, t), r.extend(n, t), n;
                      }
                      var s = l(n(312));
                      (s.Axios = i),
                        (s.create = function (e) {
                          return l(a(s.defaults, e));
                        }),
                        (s.Cancel = n(124)),
                        (s.CancelToken = n(666)),
                        (s.isCancel = n(788)),
                        (s.all = function (e) {
                          return Promise.all(e);
                        }),
                        (s.spread = n(736)),
                        (s.isAxiosError = n(487)),
                        (e.exports = s),
                        (e.exports.default = s);
                    },
                    124: function (e) {
                      "use strict";
                      function t(e) {
                        this.message = e;
                      }
                      (t.prototype.toString = function () {
                        return (
                          "Cancel" + (this.message ? ": " + this.message : "")
                        );
                      }),
                        (t.prototype.__CANCEL__ = !0),
                        (e.exports = t);
                    },
                    666: function (e, t, n) {
                      "use strict";
                      var r = n(124);
                      function o(e) {
                        if ("function" != typeof e)
                          throw new TypeError("executor must be a function.");
                        var t;
                        this.promise = new Promise(function (e) {
                          t = e;
                        });
                        var n = this;
                        e(function (e) {
                          n.reason || ((n.reason = new r(e)), t(n.reason));
                        });
                      }
                      (o.prototype.throwIfRequested = function () {
                        if (this.reason) throw this.reason;
                      }),
                        (o.source = function () {
                          var e;
                          return {
                            token: new o(function (t) {
                              e = t;
                            }),
                            cancel: e,
                          };
                        }),
                        (e.exports = o);
                    },
                    788: function (e) {
                      "use strict";
                      e.exports = function (e) {
                        return !(!e || !e.__CANCEL__);
                      };
                    },
                    595: function (e, t, n) {
                      "use strict";
                      var r = n(702),
                        o = n(996),
                        i = n(41),
                        a = n(358),
                        l = n(12),
                        s = n(158),
                        u = s.validators;
                      function c(e) {
                        (this.defaults = e),
                          (this.interceptors = {
                            request: new i(),
                            response: new i(),
                          });
                      }
                      (c.prototype.request = function (e) {
                        "string" == typeof e
                          ? ((e = arguments[1] || {}).url = arguments[0])
                          : (e = e || {}),
                          (e = l(this.defaults, e)).method
                            ? (e.method = e.method.toLowerCase())
                            : this.defaults.method
                            ? (e.method = this.defaults.method.toLowerCase())
                            : (e.method = "get");
                        var t = e.transitional;
                        void 0 !== t &&
                          s.assertOptions(
                            t,
                            {
                              silentJSONParsing: u.transitional(
                                u.boolean,
                                "1.0.0"
                              ),
                              forcedJSONParsing: u.transitional(
                                u.boolean,
                                "1.0.0"
                              ),
                              clarifyTimeoutError: u.transitional(
                                u.boolean,
                                "1.0.0"
                              ),
                            },
                            !1
                          );
                        var n = [],
                          r = !0;
                        this.interceptors.request.forEach(function (t) {
                          ("function" == typeof t.runWhen &&
                            !1 === t.runWhen(e)) ||
                            ((r = r && t.synchronous),
                            n.unshift(t.fulfilled, t.rejected));
                        });
                        var o,
                          i = [];
                        if (
                          (this.interceptors.response.forEach(function (e) {
                            i.push(e.fulfilled, e.rejected);
                          }),
                          !r)
                        ) {
                          var c = [a, void 0];
                          for (
                            Array.prototype.unshift.apply(c, n),
                              c = c.concat(i),
                              o = Promise.resolve(e);
                            c.length;

                          )
                            o = o.then(c.shift(), c.shift());
                          return o;
                        }
                        for (var f = e; n.length; ) {
                          var d = n.shift(),
                            p = n.shift();
                          try {
                            f = d(f);
                          } catch (e) {
                            p(e);
                            break;
                          }
                        }
                        try {
                          o = a(f);
                        } catch (e) {
                          return Promise.reject(e);
                        }
                        for (; i.length; ) o = o.then(i.shift(), i.shift());
                        return o;
                      }),
                        (c.prototype.getUri = function (e) {
                          return (
                            (e = l(this.defaults, e)),
                            o(e.url, e.params, e.paramsSerializer).replace(
                              /^\?/,
                              ""
                            )
                          );
                        }),
                        r.forEach(
                          ["delete", "get", "head", "options"],
                          function (e) {
                            c.prototype[e] = function (t, n) {
                              return this.request(
                                l(n || {}, {
                                  method: e,
                                  url: t,
                                  data: (n || {}).data,
                                })
                              );
                            };
                          }
                        ),
                        r.forEach(["post", "put", "patch"], function (e) {
                          c.prototype[e] = function (t, n, r) {
                            return this.request(
                              l(r || {}, { method: e, url: t, data: n })
                            );
                          };
                        }),
                        (e.exports = c);
                    },
                    41: function (e, t, n) {
                      "use strict";
                      var r = n(702);
                      function o() {
                        this.handlers = [];
                      }
                      (o.prototype.use = function (e, t, n) {
                        return (
                          this.handlers.push({
                            fulfilled: e,
                            rejected: t,
                            synchronous: !!n && n.synchronous,
                            runWhen: n ? n.runWhen : null,
                          }),
                          this.handlers.length - 1
                        );
                      }),
                        (o.prototype.eject = function (e) {
                          this.handlers[e] && (this.handlers[e] = null);
                        }),
                        (o.prototype.forEach = function (e) {
                          r.forEach(this.handlers, function (t) {
                            null !== t && e(t);
                          });
                        }),
                        (e.exports = o);
                    },
                    922: function (e, t, n) {
                      "use strict";
                      var r = n(132),
                        o = n(911);
                      e.exports = function (e, t) {
                        return e && !r(t) ? o(e, t) : t;
                      };
                    },
                    983: function (e, t, n) {
                      "use strict";
                      var r = n(328);
                      e.exports = function (e, t, n, o, i) {
                        var a = new Error(e);
                        return r(a, t, n, o, i);
                      };
                    },
                    358: function (e, t, n) {
                      "use strict";
                      var r = n(702),
                        o = n(692),
                        i = n(788),
                        a = n(312);
                      function l(e) {
                        e.cancelToken && e.cancelToken.throwIfRequested();
                      }
                      e.exports = function (e) {
                        return (
                          l(e),
                          (e.headers = e.headers || {}),
                          (e.data = o.call(
                            e,
                            e.data,
                            e.headers,
                            e.transformRequest
                          )),
                          (e.headers = r.merge(
                            e.headers.common || {},
                            e.headers[e.method] || {},
                            e.headers
                          )),
                          r.forEach(
                            [
                              "delete",
                              "get",
                              "head",
                              "post",
                              "put",
                              "patch",
                              "common",
                            ],
                            function (t) {
                              delete e.headers[t];
                            }
                          ),
                          (e.adapter || a.adapter)(e).then(
                            function (t) {
                              return (
                                l(e),
                                (t.data = o.call(
                                  e,
                                  t.data,
                                  t.headers,
                                  e.transformResponse
                                )),
                                t
                              );
                            },
                            function (t) {
                              return (
                                i(t) ||
                                  (l(e),
                                  t &&
                                    t.response &&
                                    (t.response.data = o.call(
                                      e,
                                      t.response.data,
                                      t.response.headers,
                                      e.transformResponse
                                    ))),
                                Promise.reject(t)
                              );
                            }
                          )
                        );
                      };
                    },
                    328: function (e) {
                      "use strict";
                      e.exports = function (e, t, n, r, o) {
                        return (
                          (e.config = t),
                          n && (e.code = n),
                          (e.request = r),
                          (e.response = o),
                          (e.isAxiosError = !0),
                          (e.toJSON = function () {
                            return {
                              message: this.message,
                              name: this.name,
                              description: this.description,
                              number: this.number,
                              fileName: this.fileName,
                              lineNumber: this.lineNumber,
                              columnNumber: this.columnNumber,
                              stack: this.stack,
                              config: this.config,
                              code: this.code,
                            };
                          }),
                          e
                        );
                      };
                    },
                    12: function (e, t, n) {
                      "use strict";
                      var r = n(702);
                      e.exports = function (e, t) {
                        t = t || {};
                        var n = {},
                          o = ["url", "method", "data"],
                          i = ["headers", "auth", "proxy", "params"],
                          a = [
                            "baseURL",
                            "transformRequest",
                            "transformResponse",
                            "paramsSerializer",
                            "timeout",
                            "timeoutMessage",
                            "withCredentials",
                            "adapter",
                            "responseType",
                            "xsrfCookieName",
                            "xsrfHeaderName",
                            "onUploadProgress",
                            "onDownloadProgress",
                            "decompress",
                            "maxContentLength",
                            "maxBodyLength",
                            "maxRedirects",
                            "transport",
                            "httpAgent",
                            "httpsAgent",
                            "cancelToken",
                            "socketPath",
                            "responseEncoding",
                          ],
                          l = ["validateStatus"];
                        function s(e, t) {
                          return r.isPlainObject(e) && r.isPlainObject(t)
                            ? r.merge(e, t)
                            : r.isPlainObject(t)
                            ? r.merge({}, t)
                            : r.isArray(t)
                            ? t.slice()
                            : t;
                        }
                        function u(o) {
                          r.isUndefined(t[o])
                            ? r.isUndefined(e[o]) || (n[o] = s(void 0, e[o]))
                            : (n[o] = s(e[o], t[o]));
                        }
                        r.forEach(o, function (e) {
                          r.isUndefined(t[e]) || (n[e] = s(void 0, t[e]));
                        }),
                          r.forEach(i, u),
                          r.forEach(a, function (o) {
                            r.isUndefined(t[o])
                              ? r.isUndefined(e[o]) || (n[o] = s(void 0, e[o]))
                              : (n[o] = s(void 0, t[o]));
                          }),
                          r.forEach(l, function (r) {
                            r in t
                              ? (n[r] = s(e[r], t[r]))
                              : r in e && (n[r] = s(void 0, e[r]));
                          });
                        var c = o.concat(i).concat(a).concat(l),
                          f = Object.keys(e)
                            .concat(Object.keys(t))
                            .filter(function (e) {
                              return -1 === c.indexOf(e);
                            });
                        return r.forEach(f, u), n;
                      };
                    },
                    24: function (e, t, n) {
                      "use strict";
                      var r = n(983);
                      e.exports = function (e, t, n) {
                        var o = n.config.validateStatus;
                        n.status && o && !o(n.status)
                          ? t(
                              r(
                                "Request failed with status code " + n.status,
                                n.config,
                                null,
                                n.request,
                                n
                              )
                            )
                          : e(n);
                      };
                    },
                    692: function (e, t, n) {
                      "use strict";
                      var r = n(702),
                        o = n(312);
                      e.exports = function (e, t, n) {
                        var i = this || o;
                        return (
                          r.forEach(n, function (n) {
                            e = n.call(i, e, t);
                          }),
                          e
                        );
                      };
                    },
                    312: function (e, t, n) {
                      "use strict";
                      var r = n(702),
                        o = n(582),
                        i = n(328),
                        a = {
                          "Content-Type": "application/x-www-form-urlencoded",
                        };
                      function l(e, t) {
                        !r.isUndefined(e) &&
                          r.isUndefined(e["Content-Type"]) &&
                          (e["Content-Type"] = t);
                      }
                      var s,
                        u = {
                          transitional: {
                            silentJSONParsing: !0,
                            forcedJSONParsing: !0,
                            clarifyTimeoutError: !1,
                          },
                          adapter:
                            (("undefined" != typeof XMLHttpRequest ||
                              ("undefined" != typeof process &&
                                "[object process]" ===
                                  Object.prototype.toString.call(process))) &&
                              (s = n(109)),
                            s),
                          transformRequest: [
                            function (e, t) {
                              return (
                                o(t, "Accept"),
                                o(t, "Content-Type"),
                                r.isFormData(e) ||
                                r.isArrayBuffer(e) ||
                                r.isBuffer(e) ||
                                r.isStream(e) ||
                                r.isFile(e) ||
                                r.isBlob(e)
                                  ? e
                                  : r.isArrayBufferView(e)
                                  ? e.buffer
                                  : r.isURLSearchParams(e)
                                  ? (l(
                                      t,
                                      "application/x-www-form-urlencoded;charset=utf-8"
                                    ),
                                    e.toString())
                                  : r.isObject(e) ||
                                    (t &&
                                      "application/json" === t["Content-Type"])
                                  ? (l(t, "application/json"),
                                    (function (e, t, n) {
                                      if (r.isString(e))
                                        try {
                                          return (0, JSON.parse)(e), r.trim(e);
                                        } catch (e) {
                                          if ("SyntaxError" !== e.name) throw e;
                                        }
                                      return (0, JSON.stringify)(e);
                                    })(e))
                                  : e
                              );
                            },
                          ],
                          transformResponse: [
                            function (e) {
                              var t = this.transitional,
                                n = t && t.silentJSONParsing,
                                o = t && t.forcedJSONParsing,
                                a = !n && "json" === this.responseType;
                              if (a || (o && r.isString(e) && e.length))
                                try {
                                  return JSON.parse(e);
                                } catch (e) {
                                  if (a) {
                                    if ("SyntaxError" === e.name)
                                      throw i(e, this, "E_JSON_PARSE");
                                    throw e;
                                  }
                                }
                              return e;
                            },
                          ],
                          timeout: 0,
                          xsrfCookieName: "XSRF-TOKEN",
                          xsrfHeaderName: "X-XSRF-TOKEN",
                          maxContentLength: -1,
                          maxBodyLength: -1,
                          validateStatus: function (e) {
                            return e >= 200 && e < 300;
                          },
                          headers: {
                            common: {
                              Accept: "application/json, text/plain, */*",
                            },
                          },
                        };
                      r.forEach(["delete", "get", "head"], function (e) {
                        u.headers[e] = {};
                      }),
                        r.forEach(["post", "put", "patch"], function (e) {
                          u.headers[e] = r.merge(a);
                        }),
                        (e.exports = u);
                    },
                    882: function (e) {
                      "use strict";
                      e.exports = function (e, t) {
                        return function () {
                          for (
                            var n = new Array(arguments.length), r = 0;
                            r < n.length;
                            r++
                          )
                            n[r] = arguments[r];
                          return e.apply(t, n);
                        };
                      };
                    },
                    996: function (e, t, n) {
                      "use strict";
                      var r = n(702);
                      function o(e) {
                        return encodeURIComponent(e)
                          .replace(/%3A/gi, ":")
                          .replace(/%24/g, "$")
                          .replace(/%2C/gi, ",")
                          .replace(/%20/g, "+")
                          .replace(/%5B/gi, "[")
                          .replace(/%5D/gi, "]");
                      }
                      e.exports = function (e, t, n) {
                        if (!t) return e;
                        var i;
                        if (n) i = n(t);
                        else if (r.isURLSearchParams(t)) i = t.toString();
                        else {
                          var a = [];
                          r.forEach(t, function (e, t) {
                            null != e &&
                              (r.isArray(e) ? (t += "[]") : (e = [e]),
                              r.forEach(e, function (e) {
                                r.isDate(e)
                                  ? (e = e.toISOString())
                                  : r.isObject(e) && (e = JSON.stringify(e)),
                                  a.push(o(t) + "=" + o(e));
                              }));
                          }),
                            (i = a.join("&"));
                        }
                        if (i) {
                          var l = e.indexOf("#");
                          -1 !== l && (e = e.slice(0, l)),
                            (e += (-1 === e.indexOf("?") ? "?" : "&") + i);
                        }
                        return e;
                      };
                    },
                    911: function (e) {
                      "use strict";
                      e.exports = function (e, t) {
                        return t
                          ? e.replace(/\/+$/, "") + "/" + t.replace(/^\/+/, "")
                          : e;
                      };
                    },
                    140: function (e, t, n) {
                      "use strict";
                      var r = n(702);
                      e.exports = r.isStandardBrowserEnv()
                        ? {
                            write: function (e, t, n, o, i, a) {
                              var l = [];
                              l.push(e + "=" + encodeURIComponent(t)),
                                r.isNumber(n) &&
                                  l.push(
                                    "expires=" + new Date(n).toGMTString()
                                  ),
                                r.isString(o) && l.push("path=" + o),
                                r.isString(i) && l.push("domain=" + i),
                                !0 === a && l.push("secure"),
                                (document.cookie = l.join("; "));
                            },
                            read: function (e) {
                              var t = document.cookie.match(
                                new RegExp("(^|;\\s*)(" + e + ")=([^;]*)")
                              );
                              return t ? decodeURIComponent(t[3]) : null;
                            },
                            remove: function (e) {
                              this.write(e, "", Date.now() - 864e5);
                            },
                          }
                        : {
                            write: function () {},
                            read: function () {
                              return null;
                            },
                            remove: function () {},
                          };
                    },
                    132: function (e) {
                      "use strict";
                      e.exports = function (e) {
                        return /^([a-z][a-z\d\+\-\.]*:)?\/\//i.test(e);
                      };
                    },
                    487: function (e) {
                      "use strict";
                      e.exports = function (e) {
                        return "object" == l(e) && !0 === e.isAxiosError;
                      };
                    },
                    823: function (e, t, n) {
                      "use strict";
                      var r = n(702);
                      e.exports = r.isStandardBrowserEnv()
                        ? (function () {
                            var e,
                              t = /(msie|trident)/i.test(navigator.userAgent),
                              n = document.createElement("a");
                            function o(e) {
                              var r = e;
                              return (
                                t && (n.setAttribute("href", r), (r = n.href)),
                                n.setAttribute("href", r),
                                {
                                  href: n.href,
                                  protocol: n.protocol
                                    ? n.protocol.replace(/:$/, "")
                                    : "",
                                  host: n.host,
                                  search: n.search
                                    ? n.search.replace(/^\?/, "")
                                    : "",
                                  hash: n.hash ? n.hash.replace(/^#/, "") : "",
                                  hostname: n.hostname,
                                  port: n.port,
                                  pathname:
                                    "/" === n.pathname.charAt(0)
                                      ? n.pathname
                                      : "/" + n.pathname,
                                }
                              );
                            }
                            return (
                              (e = o(window.location.href)),
                              function (t) {
                                var n = r.isString(t) ? o(t) : t;
                                return (
                                  n.protocol === e.protocol && n.host === e.host
                                );
                              }
                            );
                          })()
                        : function () {
                            return !0;
                          };
                    },
                    582: function (e, t, n) {
                      "use strict";
                      var r = n(702);
                      e.exports = function (e, t) {
                        r.forEach(e, function (n, r) {
                          r !== t &&
                            r.toUpperCase() === t.toUpperCase() &&
                            ((e[t] = n), delete e[r]);
                        });
                      };
                    },
                    254: function (e, t, n) {
                      "use strict";
                      var r = n(702),
                        o = [
                          "age",
                          "authorization",
                          "content-length",
                          "content-type",
                          "etag",
                          "expires",
                          "from",
                          "host",
                          "if-modified-since",
                          "if-unmodified-since",
                          "last-modified",
                          "location",
                          "max-forwards",
                          "proxy-authorization",
                          "referer",
                          "retry-after",
                          "user-agent",
                        ];
                      e.exports = function (e) {
                        var t,
                          n,
                          i,
                          a = {};
                        return e
                          ? (r.forEach(e.split("\n"), function (e) {
                              if (
                                ((i = e.indexOf(":")),
                                (t = r.trim(e.substr(0, i)).toLowerCase()),
                                (n = r.trim(e.substr(i + 1))),
                                t)
                              ) {
                                if (a[t] && o.indexOf(t) >= 0) return;
                                a[t] =
                                  "set-cookie" === t
                                    ? (a[t] ? a[t] : []).concat([n])
                                    : a[t]
                                    ? a[t] + ", " + n
                                    : n;
                              }
                            }),
                            a)
                          : a;
                      };
                    },
                    736: function (e) {
                      "use strict";
                      e.exports = function (e) {
                        return function (t) {
                          return e.apply(null, t);
                        };
                      };
                    },
                    158: function (e, t, n) {
                      "use strict";
                      var r = n(486),
                        o = {};
                      [
                        "object",
                        "boolean",
                        "number",
                        "function",
                        "string",
                        "symbol",
                      ].forEach(function (e, t) {
                        o[e] = function (n) {
                          return l(n) === e || "a" + (t < 1 ? "n " : " ") + e;
                        };
                      });
                      var i = {},
                        a = r.version.split(".");
                      function s(e, t) {
                        for (
                          var n = t ? t.split(".") : a, r = e.split("."), o = 0;
                          o < 3;
                          o++
                        ) {
                          if (n[o] > r[o]) return !0;
                          if (n[o] < r[o]) return !1;
                        }
                        return !1;
                      }
                      (o.transitional = function (e, t, n) {
                        var o = t && s(t);
                        function a(e, t) {
                          return (
                            "[Axios v" +
                            r.version +
                            "] Transitional option '" +
                            e +
                            "'" +
                            t +
                            (n ? ". " + n : "")
                          );
                        }
                        return function (n, r, l) {
                          if (!1 === e)
                            throw new Error(a(r, " has been removed in " + t));
                          return (
                            o &&
                              !i[r] &&
                              ((i[r] = !0),
                              console.warn(
                                a(
                                  r,
                                  " has been deprecated since v" +
                                    t +
                                    " and will be removed in the near future"
                                )
                              )),
                            !e || e(n, r, l)
                          );
                        };
                      }),
                        (e.exports = {
                          isOlderVersion: s,
                          assertOptions: function (e, t, n) {
                            if ("object" != l(e))
                              throw new TypeError("options must be an object");
                            for (
                              var r = Object.keys(e), o = r.length;
                              o-- > 0;

                            ) {
                              var i = r[o],
                                a = t[i];
                              if (a) {
                                var s = e[i],
                                  u = void 0 === s || a(s, i, e);
                                if (!0 !== u)
                                  throw new TypeError(
                                    "option " + i + " must be " + u
                                  );
                              } else if (!0 !== n)
                                throw Error("Unknown option " + i);
                            }
                          },
                          validators: o,
                        });
                    },
                    702: function (e, t, n) {
                      "use strict";
                      var r = n(882),
                        o = Object.prototype.toString;
                      function i(e) {
                        return "[object Array]" === o.call(e);
                      }
                      function a(e) {
                        return void 0 === e;
                      }
                      function s(e) {
                        return null !== e && "object" == l(e);
                      }
                      function u(e) {
                        if ("[object Object]" !== o.call(e)) return !1;
                        var t = Object.getPrototypeOf(e);
                        return null === t || t === Object.prototype;
                      }
                      function c(e) {
                        return "[object Function]" === o.call(e);
                      }
                      function f(e, t) {
                        if (null != e)
                          if (("object" != l(e) && (e = [e]), i(e)))
                            for (var n = 0, r = e.length; n < r; n++)
                              t.call(null, e[n], n, e);
                          else
                            for (var o in e)
                              Object.prototype.hasOwnProperty.call(e, o) &&
                                t.call(null, e[o], o, e);
                      }
                      e.exports = {
                        isArray: i,
                        isArrayBuffer: function (e) {
                          return "[object ArrayBuffer]" === o.call(e);
                        },
                        isBuffer: function (e) {
                          return (
                            null !== e &&
                            !a(e) &&
                            null !== e.constructor &&
                            !a(e.constructor) &&
                            "function" == typeof e.constructor.isBuffer &&
                            e.constructor.isBuffer(e)
                          );
                        },
                        isFormData: function (e) {
                          return (
                            "undefined" != typeof FormData &&
                            e instanceof FormData
                          );
                        },
                        isArrayBufferView: function (e) {
                          return "undefined" != typeof ArrayBuffer &&
                            ArrayBuffer.isView
                            ? ArrayBuffer.isView(e)
                            : e && e.buffer && e.buffer instanceof ArrayBuffer;
                        },
                        isString: function (e) {
                          return "string" == typeof e;
                        },
                        isNumber: function (e) {
                          return "number" == typeof e;
                        },
                        isObject: s,
                        isPlainObject: u,
                        isUndefined: a,
                        isDate: function (e) {
                          return "[object Date]" === o.call(e);
                        },
                        isFile: function (e) {
                          return "[object File]" === o.call(e);
                        },
                        isBlob: function (e) {
                          return "[object Blob]" === o.call(e);
                        },
                        isFunction: c,
                        isStream: function (e) {
                          return s(e) && c(e.pipe);
                        },
                        isURLSearchParams: function (e) {
                          return (
                            "undefined" != typeof URLSearchParams &&
                            e instanceof URLSearchParams
                          );
                        },
                        isStandardBrowserEnv: function () {
                          return (
                            ("undefined" == typeof navigator ||
                              ("ReactNative" !== navigator.product &&
                                "NativeScript" !== navigator.product &&
                                "NS" !== navigator.product)) &&
                            "undefined" != typeof window &&
                            "undefined" != typeof document
                          );
                        },
                        forEach: f,
                        merge: function e() {
                          var t = {};
                          function n(n, r) {
                            u(t[r]) && u(n)
                              ? (t[r] = e(t[r], n))
                              : u(n)
                              ? (t[r] = e({}, n))
                              : i(n)
                              ? (t[r] = n.slice())
                              : (t[r] = n);
                          }
                          for (var r = 0, o = arguments.length; r < o; r++)
                            f(arguments[r], n);
                          return t;
                        },
                        extend: function (e, t, n) {
                          return (
                            f(t, function (t, o) {
                              e[o] = n && "function" == typeof t ? r(t, n) : t;
                            }),
                            e
                          );
                        },
                        trim: function (e) {
                          return e.trim
                            ? e.trim()
                            : e.replace(/^\s+|\s+$/g, "");
                        },
                        stripBOM: function (e) {
                          return (
                            65279 === e.charCodeAt(0) && (e = e.slice(1)), e
                          );
                        },
                      };
                    },
                    393: function (e) {
                      e.exports = (function (e) {
                        var t = {};
                        function n(r) {
                          if (t[r]) return t[r].exports;
                          var o = (t[r] = { i: r, l: !1, exports: {} });
                          return (
                            e[r].call(o.exports, o, o.exports, n),
                            (o.l = !0),
                            o.exports
                          );
                        }
                        return (
                          (n.m = e),
                          (n.c = t),
                          (n.d = function (e, t, r) {
                            n.o(e, t) ||
                              Object.defineProperty(e, t, {
                                enumerable: !0,
                                get: r,
                              });
                          }),
                          (n.r = function (e) {
                            "undefined" != typeof Symbol &&
                              Symbol.toStringTag &&
                              Object.defineProperty(e, Symbol.toStringTag, {
                                value: "Module",
                              }),
                              Object.defineProperty(e, "__esModule", {
                                value: !0,
                              });
                          }),
                          (n.t = function (e, t) {
                            if ((1 & t && (e = n(e)), 8 & t)) return e;
                            if (4 & t && "object" == l(e) && e && e.__esModule)
                              return e;
                            var r = Object.create(null);
                            if (
                              (n.r(r),
                              Object.defineProperty(r, "default", {
                                enumerable: !0,
                                value: e,
                              }),
                              2 & t && "string" != typeof e)
                            )
                              for (var o in e)
                                n.d(
                                  r,
                                  o,
                                  function (t) {
                                    return e[t];
                                  }.bind(null, o)
                                );
                            return r;
                          }),
                          (n.n = function (e) {
                            var t =
                              e && e.__esModule
                                ? function () {
                                    return e.default;
                                  }
                                : function () {
                                    return e;
                                  };
                            return n.d(t, "a", t), t;
                          }),
                          (n.o = function (e, t) {
                            return Object.prototype.hasOwnProperty.call(e, t);
                          }),
                          (n.p = ""),
                          n((n.s = 90))
                        );
                      })({
                        17: function (e, t, n) {
                          "use strict";
                          (t.__esModule = !0), (t.default = void 0);
                          var r = n(18),
                            o = (function () {
                              function e() {}
                              return (
                                (e.getFirstMatch = function (e, t) {
                                  var n = t.match(e);
                                  return (n && n.length > 0 && n[1]) || "";
                                }),
                                (e.getSecondMatch = function (e, t) {
                                  var n = t.match(e);
                                  return (n && n.length > 1 && n[2]) || "";
                                }),
                                (e.matchAndReturnConst = function (e, t, n) {
                                  if (e.test(t)) return n;
                                }),
                                (e.getWindowsVersionName = function (e) {
                                  switch (e) {
                                    case "NT":
                                      return "NT";
                                    case "XP":
                                    case "NT 5.1":
                                      return "XP";
                                    case "NT 5.0":
                                      return "2000";
                                    case "NT 5.2":
                                      return "2003";
                                    case "NT 6.0":
                                      return "Vista";
                                    case "NT 6.1":
                                      return "7";
                                    case "NT 6.2":
                                      return "8";
                                    case "NT 6.3":
                                      return "8.1";
                                    case "NT 10.0":
                                      return "10";
                                    default:
                                      return;
                                  }
                                }),
                                (e.getMacOSVersionName = function (e) {
                                  var t = e
                                    .split(".")
                                    .splice(0, 2)
                                    .map(function (e) {
                                      return parseInt(e, 10) || 0;
                                    });
                                  if ((t.push(0), 10 === t[0]))
                                    switch (t[1]) {
                                      case 5:
                                        return "Leopard";
                                      case 6:
                                        return "Snow Leopard";
                                      case 7:
                                        return "Lion";
                                      case 8:
                                        return "Mountain Lion";
                                      case 9:
                                        return "Mavericks";
                                      case 10:
                                        return "Yosemite";
                                      case 11:
                                        return "El Capitan";
                                      case 12:
                                        return "Sierra";
                                      case 13:
                                        return "High Sierra";
                                      case 14:
                                        return "Mojave";
                                      case 15:
                                        return "Catalina";
                                      default:
                                        return;
                                    }
                                }),
                                (e.getAndroidVersionName = function (e) {
                                  var t = e
                                    .split(".")
                                    .splice(0, 2)
                                    .map(function (e) {
                                      return parseInt(e, 10) || 0;
                                    });
                                  if ((t.push(0), !(1 === t[0] && t[1] < 5)))
                                    return 1 === t[0] && t[1] < 6
                                      ? "Cupcake"
                                      : 1 === t[0] && t[1] >= 6
                                      ? "Donut"
                                      : 2 === t[0] && t[1] < 2
                                      ? "Eclair"
                                      : 2 === t[0] && 2 === t[1]
                                      ? "Froyo"
                                      : 2 === t[0] && t[1] > 2
                                      ? "Gingerbread"
                                      : 3 === t[0]
                                      ? "Honeycomb"
                                      : 4 === t[0] && t[1] < 1
                                      ? "Ice Cream Sandwich"
                                      : 4 === t[0] && t[1] < 4
                                      ? "Jelly Bean"
                                      : 4 === t[0] && t[1] >= 4
                                      ? "KitKat"
                                      : 5 === t[0]
                                      ? "Lollipop"
                                      : 6 === t[0]
                                      ? "Marshmallow"
                                      : 7 === t[0]
                                      ? "Nougat"
                                      : 8 === t[0]
                                      ? "Oreo"
                                      : 9 === t[0]
                                      ? "Pie"
                                      : void 0;
                                }),
                                (e.getVersionPrecision = function (e) {
                                  return e.split(".").length;
                                }),
                                (e.compareVersions = function (t, n, r) {
                                  void 0 === r && (r = !1);
                                  var o = e.getVersionPrecision(t),
                                    i = e.getVersionPrecision(n),
                                    a = Math.max(o, i),
                                    l = 0,
                                    s = e.map([t, n], function (t) {
                                      var n = a - e.getVersionPrecision(t),
                                        r = t + new Array(n + 1).join(".0");
                                      return e
                                        .map(r.split("."), function (e) {
                                          return (
                                            new Array(20 - e.length).join("0") +
                                            e
                                          );
                                        })
                                        .reverse();
                                    });
                                  for (
                                    r && (l = a - Math.min(o, i)), a -= 1;
                                    a >= l;

                                  ) {
                                    if (s[0][a] > s[1][a]) return 1;
                                    if (s[0][a] === s[1][a]) {
                                      if (a === l) return 0;
                                      a -= 1;
                                    } else if (s[0][a] < s[1][a]) return -1;
                                  }
                                }),
                                (e.map = function (e, t) {
                                  var n,
                                    r = [];
                                  if (Array.prototype.map)
                                    return Array.prototype.map.call(e, t);
                                  for (n = 0; n < e.length; n += 1)
                                    r.push(t(e[n]));
                                  return r;
                                }),
                                (e.find = function (e, t) {
                                  var n, r;
                                  if (Array.prototype.find)
                                    return Array.prototype.find.call(e, t);
                                  for (n = 0, r = e.length; n < r; n += 1) {
                                    var o = e[n];
                                    if (t(o, n)) return o;
                                  }
                                }),
                                (e.assign = function (e) {
                                  for (
                                    var t,
                                      n,
                                      r = e,
                                      o = arguments.length,
                                      i = new Array(o > 1 ? o - 1 : 0),
                                      a = 1;
                                    a < o;
                                    a++
                                  )
                                    i[a - 1] = arguments[a];
                                  if (Object.assign)
                                    return Object.assign.apply(
                                      Object,
                                      [e].concat(i)
                                    );
                                  var s = function () {
                                    var e = i[t];
                                    "object" == l(e) &&
                                      null !== e &&
                                      Object.keys(e).forEach(function (t) {
                                        r[t] = e[t];
                                      });
                                  };
                                  for (t = 0, n = i.length; t < n; t += 1) s();
                                  return e;
                                }),
                                (e.getBrowserAlias = function (e) {
                                  return r.BROWSER_ALIASES_MAP[e];
                                }),
                                (e.getBrowserTypeByAlias = function (e) {
                                  return r.BROWSER_MAP[e] || "";
                                }),
                                e
                              );
                            })();
                          (t.default = o), (e.exports = t.default);
                        },
                        18: function (e, t, n) {
                          "use strict";
                          (t.__esModule = !0),
                            (t.ENGINE_MAP = t.OS_MAP = t.PLATFORMS_MAP = t.BROWSER_MAP = t.BROWSER_ALIASES_MAP = void 0),
                            (t.BROWSER_ALIASES_MAP = {
                              "Amazon Silk": "amazon_silk",
                              "Android Browser": "android",
                              Bada: "bada",
                              BlackBerry: "blackberry",
                              Chrome: "chrome",
                              Chromium: "chromium",
                              Electron: "electron",
                              Epiphany: "epiphany",
                              Firefox: "firefox",
                              Focus: "focus",
                              Generic: "generic",
                              "Google Search": "google_search",
                              Googlebot: "googlebot",
                              "Internet Explorer": "ie",
                              "K-Meleon": "k_meleon",
                              Maxthon: "maxthon",
                              "Microsoft Edge": "edge",
                              "MZ Browser": "mz",
                              "NAVER Whale Browser": "naver",
                              Opera: "opera",
                              "Opera Coast": "opera_coast",
                              PhantomJS: "phantomjs",
                              Puffin: "puffin",
                              QupZilla: "qupzilla",
                              QQ: "qq",
                              QQLite: "qqlite",
                              Safari: "safari",
                              Sailfish: "sailfish",
                              "Samsung Internet for Android":
                                "samsung_internet",
                              SeaMonkey: "seamonkey",
                              Sleipnir: "sleipnir",
                              Swing: "swing",
                              Tizen: "tizen",
                              "UC Browser": "uc",
                              Vivaldi: "vivaldi",
                              "WebOS Browser": "webos",
                              WeChat: "wechat",
                              "Yandex Browser": "yandex",
                              Roku: "roku",
                            }),
                            (t.BROWSER_MAP = {
                              amazon_silk: "Amazon Silk",
                              android: "Android Browser",
                              bada: "Bada",
                              blackberry: "BlackBerry",
                              chrome: "Chrome",
                              chromium: "Chromium",
                              electron: "Electron",
                              epiphany: "Epiphany",
                              firefox: "Firefox",
                              focus: "Focus",
                              generic: "Generic",
                              googlebot: "Googlebot",
                              google_search: "Google Search",
                              ie: "Internet Explorer",
                              k_meleon: "K-Meleon",
                              maxthon: "Maxthon",
                              edge: "Microsoft Edge",
                              mz: "MZ Browser",
                              naver: "NAVER Whale Browser",
                              opera: "Opera",
                              opera_coast: "Opera Coast",
                              phantomjs: "PhantomJS",
                              puffin: "Puffin",
                              qupzilla: "QupZilla",
                              qq: "QQ Browser",
                              qqlite: "QQ Browser Lite",
                              safari: "Safari",
                              sailfish: "Sailfish",
                              samsung_internet: "Samsung Internet for Android",
                              seamonkey: "SeaMonkey",
                              sleipnir: "Sleipnir",
                              swing: "Swing",
                              tizen: "Tizen",
                              uc: "UC Browser",
                              vivaldi: "Vivaldi",
                              webos: "WebOS Browser",
                              wechat: "WeChat",
                              yandex: "Yandex Browser",
                            }),
                            (t.PLATFORMS_MAP = {
                              tablet: "tablet",
                              mobile: "mobile",
                              desktop: "desktop",
                              tv: "tv",
                            }),
                            (t.OS_MAP = {
                              WindowsPhone: "Windows Phone",
                              Windows: "Windows",
                              MacOS: "macOS",
                              iOS: "iOS",
                              Android: "Android",
                              WebOS: "WebOS",
                              BlackBerry: "BlackBerry",
                              Bada: "Bada",
                              Tizen: "Tizen",
                              Linux: "Linux",
                              ChromeOS: "Chrome OS",
                              PlayStation4: "PlayStation 4",
                              Roku: "Roku",
                            }),
                            (t.ENGINE_MAP = {
                              EdgeHTML: "EdgeHTML",
                              Blink: "Blink",
                              Trident: "Trident",
                              Presto: "Presto",
                              Gecko: "Gecko",
                              WebKit: "WebKit",
                            });
                        },
                        90: function (e, t, n) {
                          "use strict";
                          (t.__esModule = !0), (t.default = void 0);
                          var r,
                            o =
                              (r = n(91)) && r.__esModule ? r : { default: r },
                            i = n(18),
                            a = (function () {
                              function e() {}
                              var t;
                              return (
                                (e.getParser = function (e, t) {
                                  if (
                                    (void 0 === t && (t = !1),
                                    "string" != typeof e)
                                  )
                                    throw new Error(
                                      "UserAgent should be a string"
                                    );
                                  return new o.default(e, t);
                                }),
                                (e.parse = function (e) {
                                  return new o.default(e).getResult();
                                }),
                                (t = [
                                  {
                                    key: "BROWSER_MAP",
                                    get: function () {
                                      return i.BROWSER_MAP;
                                    },
                                  },
                                  {
                                    key: "ENGINE_MAP",
                                    get: function () {
                                      return i.ENGINE_MAP;
                                    },
                                  },
                                  {
                                    key: "OS_MAP",
                                    get: function () {
                                      return i.OS_MAP;
                                    },
                                  },
                                  {
                                    key: "PLATFORMS_MAP",
                                    get: function () {
                                      return i.PLATFORMS_MAP;
                                    },
                                  },
                                ]) &&
                                  (function (e, t) {
                                    for (var n = 0; n < t.length; n++) {
                                      var r = t[n];
                                      (r.enumerable = r.enumerable || !1),
                                        (r.configurable = !0),
                                        "value" in r && (r.writable = !0),
                                        Object.defineProperty(e, r.key, r);
                                    }
                                  })(e, t),
                                e
                              );
                            })();
                          (t.default = a), (e.exports = t.default);
                        },
                        91: function (e, t, n) {
                          "use strict";
                          (t.__esModule = !0), (t.default = void 0);
                          var r = u(n(92)),
                            o = u(n(93)),
                            i = u(n(94)),
                            a = u(n(95)),
                            s = u(n(17));
                          function u(e) {
                            return e && e.__esModule ? e : { default: e };
                          }
                          var c = (function () {
                            function e(e, t) {
                              if (
                                (void 0 === t && (t = !1),
                                null == e || "" === e)
                              )
                                throw new Error(
                                  "UserAgent parameter can't be empty"
                                );
                              (this._ua = e),
                                (this.parsedResult = {}),
                                !0 !== t && this.parse();
                            }
                            var t = e.prototype;
                            return (
                              (t.getUA = function () {
                                return this._ua;
                              }),
                              (t.test = function (e) {
                                return e.test(this._ua);
                              }),
                              (t.parseBrowser = function () {
                                var e = this;
                                this.parsedResult.browser = {};
                                var t = s.default.find(r.default, function (t) {
                                  if ("function" == typeof t.test)
                                    return t.test(e);
                                  if (t.test instanceof Array)
                                    return t.test.some(function (t) {
                                      return e.test(t);
                                    });
                                  throw new Error(
                                    "Browser's test function is not valid"
                                  );
                                });
                                return (
                                  t &&
                                    (this.parsedResult.browser = t.describe(
                                      this.getUA()
                                    )),
                                  this.parsedResult.browser
                                );
                              }),
                              (t.getBrowser = function () {
                                return this.parsedResult.browser
                                  ? this.parsedResult.browser
                                  : this.parseBrowser();
                              }),
                              (t.getBrowserName = function (e) {
                                return e
                                  ? String(
                                      this.getBrowser().name
                                    ).toLowerCase() || ""
                                  : this.getBrowser().name || "";
                              }),
                              (t.getBrowserVersion = function () {
                                return this.getBrowser().version;
                              }),
                              (t.getOS = function () {
                                return this.parsedResult.os
                                  ? this.parsedResult.os
                                  : this.parseOS();
                              }),
                              (t.parseOS = function () {
                                var e = this;
                                this.parsedResult.os = {};
                                var t = s.default.find(o.default, function (t) {
                                  if ("function" == typeof t.test)
                                    return t.test(e);
                                  if (t.test instanceof Array)
                                    return t.test.some(function (t) {
                                      return e.test(t);
                                    });
                                  throw new Error(
                                    "Browser's test function is not valid"
                                  );
                                });
                                return (
                                  t &&
                                    (this.parsedResult.os = t.describe(
                                      this.getUA()
                                    )),
                                  this.parsedResult.os
                                );
                              }),
                              (t.getOSName = function (e) {
                                var t = this.getOS().name;
                                return e
                                  ? String(t).toLowerCase() || ""
                                  : t || "";
                              }),
                              (t.getOSVersion = function () {
                                return this.getOS().version;
                              }),
                              (t.getPlatform = function () {
                                return this.parsedResult.platform
                                  ? this.parsedResult.platform
                                  : this.parsePlatform();
                              }),
                              (t.getPlatformType = function (e) {
                                void 0 === e && (e = !1);
                                var t = this.getPlatform().type;
                                return e
                                  ? String(t).toLowerCase() || ""
                                  : t || "";
                              }),
                              (t.parsePlatform = function () {
                                var e = this;
                                this.parsedResult.platform = {};
                                var t = s.default.find(i.default, function (t) {
                                  if ("function" == typeof t.test)
                                    return t.test(e);
                                  if (t.test instanceof Array)
                                    return t.test.some(function (t) {
                                      return e.test(t);
                                    });
                                  throw new Error(
                                    "Browser's test function is not valid"
                                  );
                                });
                                return (
                                  t &&
                                    (this.parsedResult.platform = t.describe(
                                      this.getUA()
                                    )),
                                  this.parsedResult.platform
                                );
                              }),
                              (t.getEngine = function () {
                                return this.parsedResult.engine
                                  ? this.parsedResult.engine
                                  : this.parseEngine();
                              }),
                              (t.getEngineName = function (e) {
                                return e
                                  ? String(
                                      this.getEngine().name
                                    ).toLowerCase() || ""
                                  : this.getEngine().name || "";
                              }),
                              (t.parseEngine = function () {
                                var e = this;
                                this.parsedResult.engine = {};
                                var t = s.default.find(a.default, function (t) {
                                  if ("function" == typeof t.test)
                                    return t.test(e);
                                  if (t.test instanceof Array)
                                    return t.test.some(function (t) {
                                      return e.test(t);
                                    });
                                  throw new Error(
                                    "Browser's test function is not valid"
                                  );
                                });
                                return (
                                  t &&
                                    (this.parsedResult.engine = t.describe(
                                      this.getUA()
                                    )),
                                  this.parsedResult.engine
                                );
                              }),
                              (t.parse = function () {
                                return (
                                  this.parseBrowser(),
                                  this.parseOS(),
                                  this.parsePlatform(),
                                  this.parseEngine(),
                                  this
                                );
                              }),
                              (t.getResult = function () {
                                return s.default.assign({}, this.parsedResult);
                              }),
                              (t.satisfies = function (e) {
                                var t = this,
                                  n = {},
                                  r = 0,
                                  o = {},
                                  i = 0;
                                if (
                                  (Object.keys(e).forEach(function (t) {
                                    var a = e[t];
                                    "string" == typeof a
                                      ? ((o[t] = a), (i += 1))
                                      : "object" == l(a) &&
                                        ((n[t] = a), (r += 1));
                                  }),
                                  r > 0)
                                ) {
                                  var a = Object.keys(n),
                                    u = s.default.find(a, function (e) {
                                      return t.isOS(e);
                                    });
                                  if (u) {
                                    var c = this.satisfies(n[u]);
                                    if (void 0 !== c) return c;
                                  }
                                  var f = s.default.find(a, function (e) {
                                    return t.isPlatform(e);
                                  });
                                  if (f) {
                                    var d = this.satisfies(n[f]);
                                    if (void 0 !== d) return d;
                                  }
                                }
                                if (i > 0) {
                                  var p = Object.keys(o),
                                    m = s.default.find(p, function (e) {
                                      return t.isBrowser(e, !0);
                                    });
                                  if (void 0 !== m)
                                    return this.compareVersion(o[m]);
                                }
                              }),
                              (t.isBrowser = function (e, t) {
                                void 0 === t && (t = !1);
                                var n = this.getBrowserName().toLowerCase(),
                                  r = e.toLowerCase(),
                                  o = s.default.getBrowserTypeByAlias(r);
                                return t && o && (r = o.toLowerCase()), r === n;
                              }),
                              (t.compareVersion = function (e) {
                                var t = [0],
                                  n = e,
                                  r = !1,
                                  o = this.getBrowserVersion();
                                if ("string" == typeof o)
                                  return (
                                    ">" === e[0] || "<" === e[0]
                                      ? ((n = e.substr(1)),
                                        "=" === e[1]
                                          ? ((r = !0), (n = e.substr(2)))
                                          : (t = []),
                                        ">" === e[0] ? t.push(1) : t.push(-1))
                                      : "=" === e[0]
                                      ? (n = e.substr(1))
                                      : "~" === e[0] &&
                                        ((r = !0), (n = e.substr(1))),
                                    t.indexOf(
                                      s.default.compareVersions(o, n, r)
                                    ) > -1
                                  );
                              }),
                              (t.isOS = function (e) {
                                return (
                                  this.getOSName(!0) === String(e).toLowerCase()
                                );
                              }),
                              (t.isPlatform = function (e) {
                                return (
                                  this.getPlatformType(!0) ===
                                  String(e).toLowerCase()
                                );
                              }),
                              (t.isEngine = function (e) {
                                return (
                                  this.getEngineName(!0) ===
                                  String(e).toLowerCase()
                                );
                              }),
                              (t.is = function (e, t) {
                                return (
                                  void 0 === t && (t = !1),
                                  this.isBrowser(e, t) ||
                                    this.isOS(e) ||
                                    this.isPlatform(e)
                                );
                              }),
                              (t.some = function (e) {
                                var t = this;
                                return (
                                  void 0 === e && (e = []),
                                  e.some(function (e) {
                                    return t.is(e);
                                  })
                                );
                              }),
                              e
                            );
                          })();
                          (t.default = c), (e.exports = t.default);
                        },
                        92: function (e, t, n) {
                          "use strict";
                          (t.__esModule = !0), (t.default = void 0);
                          var r,
                            o =
                              (r = n(17)) && r.__esModule ? r : { default: r },
                            i = /version\/(\d+(\.?_?\d+)+)/i,
                            a = [
                              {
                                test: [/googlebot/i],
                                describe: function (e) {
                                  var t = { name: "Googlebot" },
                                    n =
                                      o.default.getFirstMatch(
                                        /googlebot\/(\d+(\.\d+))/i,
                                        e
                                      ) || o.default.getFirstMatch(i, e);
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/opera/i],
                                describe: function (e) {
                                  var t = { name: "Opera" },
                                    n =
                                      o.default.getFirstMatch(i, e) ||
                                      o.default.getFirstMatch(
                                        /(?:opera)[\s/](\d+(\.?_?\d+)+)/i,
                                        e
                                      );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/opr\/|opios/i],
                                describe: function (e) {
                                  var t = { name: "Opera" },
                                    n =
                                      o.default.getFirstMatch(
                                        /(?:opr|opios)[\s/](\S+)/i,
                                        e
                                      ) || o.default.getFirstMatch(i, e);
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/SamsungBrowser/i],
                                describe: function (e) {
                                  var t = {
                                      name: "Samsung Internet for Android",
                                    },
                                    n =
                                      o.default.getFirstMatch(i, e) ||
                                      o.default.getFirstMatch(
                                        /(?:SamsungBrowser)[\s/](\d+(\.?_?\d+)+)/i,
                                        e
                                      );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/Whale/i],
                                describe: function (e) {
                                  var t = { name: "NAVER Whale Browser" },
                                    n =
                                      o.default.getFirstMatch(i, e) ||
                                      o.default.getFirstMatch(
                                        /(?:whale)[\s/](\d+(?:\.\d+)+)/i,
                                        e
                                      );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/MZBrowser/i],
                                describe: function (e) {
                                  var t = { name: "MZ Browser" },
                                    n =
                                      o.default.getFirstMatch(
                                        /(?:MZBrowser)[\s/](\d+(?:\.\d+)+)/i,
                                        e
                                      ) || o.default.getFirstMatch(i, e);
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/focus/i],
                                describe: function (e) {
                                  var t = { name: "Focus" },
                                    n =
                                      o.default.getFirstMatch(
                                        /(?:focus)[\s/](\d+(?:\.\d+)+)/i,
                                        e
                                      ) || o.default.getFirstMatch(i, e);
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/swing/i],
                                describe: function (e) {
                                  var t = { name: "Swing" },
                                    n =
                                      o.default.getFirstMatch(
                                        /(?:swing)[\s/](\d+(?:\.\d+)+)/i,
                                        e
                                      ) || o.default.getFirstMatch(i, e);
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/coast/i],
                                describe: function (e) {
                                  var t = { name: "Opera Coast" },
                                    n =
                                      o.default.getFirstMatch(i, e) ||
                                      o.default.getFirstMatch(
                                        /(?:coast)[\s/](\d+(\.?_?\d+)+)/i,
                                        e
                                      );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/opt\/\d+(?:.?_?\d+)+/i],
                                describe: function (e) {
                                  var t = { name: "Opera Touch" },
                                    n =
                                      o.default.getFirstMatch(
                                        /(?:opt)[\s/](\d+(\.?_?\d+)+)/i,
                                        e
                                      ) || o.default.getFirstMatch(i, e);
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/yabrowser/i],
                                describe: function (e) {
                                  var t = { name: "Yandex Browser" },
                                    n =
                                      o.default.getFirstMatch(
                                        /(?:yabrowser)[\s/](\d+(\.?_?\d+)+)/i,
                                        e
                                      ) || o.default.getFirstMatch(i, e);
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/ucbrowser/i],
                                describe: function (e) {
                                  var t = { name: "UC Browser" },
                                    n =
                                      o.default.getFirstMatch(i, e) ||
                                      o.default.getFirstMatch(
                                        /(?:ucbrowser)[\s/](\d+(\.?_?\d+)+)/i,
                                        e
                                      );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/Maxthon|mxios/i],
                                describe: function (e) {
                                  var t = { name: "Maxthon" },
                                    n =
                                      o.default.getFirstMatch(i, e) ||
                                      o.default.getFirstMatch(
                                        /(?:Maxthon|mxios)[\s/](\d+(\.?_?\d+)+)/i,
                                        e
                                      );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/epiphany/i],
                                describe: function (e) {
                                  var t = { name: "Epiphany" },
                                    n =
                                      o.default.getFirstMatch(i, e) ||
                                      o.default.getFirstMatch(
                                        /(?:epiphany)[\s/](\d+(\.?_?\d+)+)/i,
                                        e
                                      );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/puffin/i],
                                describe: function (e) {
                                  var t = { name: "Puffin" },
                                    n =
                                      o.default.getFirstMatch(i, e) ||
                                      o.default.getFirstMatch(
                                        /(?:puffin)[\s/](\d+(\.?_?\d+)+)/i,
                                        e
                                      );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/sleipnir/i],
                                describe: function (e) {
                                  var t = { name: "Sleipnir" },
                                    n =
                                      o.default.getFirstMatch(i, e) ||
                                      o.default.getFirstMatch(
                                        /(?:sleipnir)[\s/](\d+(\.?_?\d+)+)/i,
                                        e
                                      );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/k-meleon/i],
                                describe: function (e) {
                                  var t = { name: "K-Meleon" },
                                    n =
                                      o.default.getFirstMatch(i, e) ||
                                      o.default.getFirstMatch(
                                        /(?:k-meleon)[\s/](\d+(\.?_?\d+)+)/i,
                                        e
                                      );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/micromessenger/i],
                                describe: function (e) {
                                  var t = { name: "WeChat" },
                                    n =
                                      o.default.getFirstMatch(
                                        /(?:micromessenger)[\s/](\d+(\.?_?\d+)+)/i,
                                        e
                                      ) || o.default.getFirstMatch(i, e);
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/qqbrowser/i],
                                describe: function (e) {
                                  var t = {
                                      name: /qqbrowserlite/i.test(e)
                                        ? "QQ Browser Lite"
                                        : "QQ Browser",
                                    },
                                    n =
                                      o.default.getFirstMatch(
                                        /(?:qqbrowserlite|qqbrowser)[/](\d+(\.?_?\d+)+)/i,
                                        e
                                      ) || o.default.getFirstMatch(i, e);
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/msie|trident/i],
                                describe: function (e) {
                                  var t = { name: "Internet Explorer" },
                                    n = o.default.getFirstMatch(
                                      /(?:msie |rv:)(\d+(\.?_?\d+)+)/i,
                                      e
                                    );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/\sedg\//i],
                                describe: function (e) {
                                  var t = { name: "Microsoft Edge" },
                                    n = o.default.getFirstMatch(
                                      /\sedg\/(\d+(\.?_?\d+)+)/i,
                                      e
                                    );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/edg([ea]|ios)/i],
                                describe: function (e) {
                                  var t = { name: "Microsoft Edge" },
                                    n = o.default.getSecondMatch(
                                      /edg([ea]|ios)\/(\d+(\.?_?\d+)+)/i,
                                      e
                                    );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/vivaldi/i],
                                describe: function (e) {
                                  var t = { name: "Vivaldi" },
                                    n = o.default.getFirstMatch(
                                      /vivaldi\/(\d+(\.?_?\d+)+)/i,
                                      e
                                    );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/seamonkey/i],
                                describe: function (e) {
                                  var t = { name: "SeaMonkey" },
                                    n = o.default.getFirstMatch(
                                      /seamonkey\/(\d+(\.?_?\d+)+)/i,
                                      e
                                    );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/sailfish/i],
                                describe: function (e) {
                                  var t = { name: "Sailfish" },
                                    n = o.default.getFirstMatch(
                                      /sailfish\s?browser\/(\d+(\.\d+)?)/i,
                                      e
                                    );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/silk/i],
                                describe: function (e) {
                                  var t = { name: "Amazon Silk" },
                                    n = o.default.getFirstMatch(
                                      /silk\/(\d+(\.?_?\d+)+)/i,
                                      e
                                    );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/phantom/i],
                                describe: function (e) {
                                  var t = { name: "PhantomJS" },
                                    n = o.default.getFirstMatch(
                                      /phantomjs\/(\d+(\.?_?\d+)+)/i,
                                      e
                                    );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/slimerjs/i],
                                describe: function (e) {
                                  var t = { name: "SlimerJS" },
                                    n = o.default.getFirstMatch(
                                      /slimerjs\/(\d+(\.?_?\d+)+)/i,
                                      e
                                    );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/blackberry|\bbb\d+/i, /rim\stablet/i],
                                describe: function (e) {
                                  var t = { name: "BlackBerry" },
                                    n =
                                      o.default.getFirstMatch(i, e) ||
                                      o.default.getFirstMatch(
                                        /blackberry[\d]+\/(\d+(\.?_?\d+)+)/i,
                                        e
                                      );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/(web|hpw)[o0]s/i],
                                describe: function (e) {
                                  var t = { name: "WebOS Browser" },
                                    n =
                                      o.default.getFirstMatch(i, e) ||
                                      o.default.getFirstMatch(
                                        /w(?:eb)?[o0]sbrowser\/(\d+(\.?_?\d+)+)/i,
                                        e
                                      );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/bada/i],
                                describe: function (e) {
                                  var t = { name: "Bada" },
                                    n = o.default.getFirstMatch(
                                      /dolfin\/(\d+(\.?_?\d+)+)/i,
                                      e
                                    );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/tizen/i],
                                describe: function (e) {
                                  var t = { name: "Tizen" },
                                    n =
                                      o.default.getFirstMatch(
                                        /(?:tizen\s?)?browser\/(\d+(\.?_?\d+)+)/i,
                                        e
                                      ) || o.default.getFirstMatch(i, e);
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/qupzilla/i],
                                describe: function (e) {
                                  var t = { name: "QupZilla" },
                                    n =
                                      o.default.getFirstMatch(
                                        /(?:qupzilla)[\s/](\d+(\.?_?\d+)+)/i,
                                        e
                                      ) || o.default.getFirstMatch(i, e);
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/firefox|iceweasel|fxios/i],
                                describe: function (e) {
                                  var t = { name: "Firefox" },
                                    n = o.default.getFirstMatch(
                                      /(?:firefox|iceweasel|fxios)[\s/](\d+(\.?_?\d+)+)/i,
                                      e
                                    );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/electron/i],
                                describe: function (e) {
                                  var t = { name: "Electron" },
                                    n = o.default.getFirstMatch(
                                      /(?:electron)\/(\d+(\.?_?\d+)+)/i,
                                      e
                                    );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/MiuiBrowser/i],
                                describe: function (e) {
                                  var t = { name: "Miui" },
                                    n = o.default.getFirstMatch(
                                      /(?:MiuiBrowser)[\s/](\d+(\.?_?\d+)+)/i,
                                      e
                                    );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/chromium/i],
                                describe: function (e) {
                                  var t = { name: "Chromium" },
                                    n =
                                      o.default.getFirstMatch(
                                        /(?:chromium)[\s/](\d+(\.?_?\d+)+)/i,
                                        e
                                      ) || o.default.getFirstMatch(i, e);
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/chrome|crios|crmo/i],
                                describe: function (e) {
                                  var t = { name: "Chrome" },
                                    n = o.default.getFirstMatch(
                                      /(?:chrome|crios|crmo)\/(\d+(\.?_?\d+)+)/i,
                                      e
                                    );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/GSA/i],
                                describe: function (e) {
                                  var t = { name: "Google Search" },
                                    n = o.default.getFirstMatch(
                                      /(?:GSA)\/(\d+(\.?_?\d+)+)/i,
                                      e
                                    );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: function (e) {
                                  var t = !e.test(/like android/i),
                                    n = e.test(/android/i);
                                  return t && n;
                                },
                                describe: function (e) {
                                  var t = { name: "Android Browser" },
                                    n = o.default.getFirstMatch(i, e);
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/playstation 4/i],
                                describe: function (e) {
                                  var t = { name: "PlayStation 4" },
                                    n = o.default.getFirstMatch(i, e);
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/safari|applewebkit/i],
                                describe: function (e) {
                                  var t = { name: "Safari" },
                                    n = o.default.getFirstMatch(i, e);
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/.*/i],
                                describe: function (e) {
                                  var t =
                                    -1 !== e.search("\\(")
                                      ? /^(.*)\/(.*)[ \t]\((.*)/
                                      : /^(.*)\/(.*) /;
                                  return {
                                    name: o.default.getFirstMatch(t, e),
                                    version: o.default.getSecondMatch(t, e),
                                  };
                                },
                              },
                            ];
                          (t.default = a), (e.exports = t.default);
                        },
                        93: function (e, t, n) {
                          "use strict";
                          (t.__esModule = !0), (t.default = void 0);
                          var r,
                            o =
                              (r = n(17)) && r.__esModule ? r : { default: r },
                            i = n(18),
                            a = [
                              {
                                test: [/Roku\/DVP/],
                                describe: function (e) {
                                  var t = o.default.getFirstMatch(
                                    /Roku\/DVP-(\d+\.\d+)/i,
                                    e
                                  );
                                  return { name: i.OS_MAP.Roku, version: t };
                                },
                              },
                              {
                                test: [/windows phone/i],
                                describe: function (e) {
                                  var t = o.default.getFirstMatch(
                                    /windows phone (?:os)?\s?(\d+(\.\d+)*)/i,
                                    e
                                  );
                                  return {
                                    name: i.OS_MAP.WindowsPhone,
                                    version: t,
                                  };
                                },
                              },
                              {
                                test: [/windows /i],
                                describe: function (e) {
                                  var t = o.default.getFirstMatch(
                                      /Windows ((NT|XP)( \d\d?.\d)?)/i,
                                      e
                                    ),
                                    n = o.default.getWindowsVersionName(t);
                                  return {
                                    name: i.OS_MAP.Windows,
                                    version: t,
                                    versionName: n,
                                  };
                                },
                              },
                              {
                                test: [/Macintosh(.*?) FxiOS(.*?)\//],
                                describe: function (e) {
                                  var t = { name: i.OS_MAP.iOS },
                                    n = o.default.getSecondMatch(
                                      /(Version\/)(\d[\d.]+)/,
                                      e
                                    );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/macintosh/i],
                                describe: function (e) {
                                  var t = o.default
                                      .getFirstMatch(
                                        /mac os x (\d+(\.?_?\d+)+)/i,
                                        e
                                      )
                                      .replace(/[_\s]/g, "."),
                                    n = o.default.getMacOSVersionName(t),
                                    r = { name: i.OS_MAP.MacOS, version: t };
                                  return n && (r.versionName = n), r;
                                },
                              },
                              {
                                test: [/(ipod|iphone|ipad)/i],
                                describe: function (e) {
                                  var t = o.default
                                    .getFirstMatch(
                                      /os (\d+([_\s]\d+)*) like mac os x/i,
                                      e
                                    )
                                    .replace(/[_\s]/g, ".");
                                  return { name: i.OS_MAP.iOS, version: t };
                                },
                              },
                              {
                                test: function (e) {
                                  var t = !e.test(/like android/i),
                                    n = e.test(/android/i);
                                  return t && n;
                                },
                                describe: function (e) {
                                  var t = o.default.getFirstMatch(
                                      /android[\s/-](\d+(\.\d+)*)/i,
                                      e
                                    ),
                                    n = o.default.getAndroidVersionName(t),
                                    r = { name: i.OS_MAP.Android, version: t };
                                  return n && (r.versionName = n), r;
                                },
                              },
                              {
                                test: [/(web|hpw)[o0]s/i],
                                describe: function (e) {
                                  var t = o.default.getFirstMatch(
                                      /(?:web|hpw)[o0]s\/(\d+(\.\d+)*)/i,
                                      e
                                    ),
                                    n = { name: i.OS_MAP.WebOS };
                                  return t && t.length && (n.version = t), n;
                                },
                              },
                              {
                                test: [/blackberry|\bbb\d+/i, /rim\stablet/i],
                                describe: function (e) {
                                  var t =
                                    o.default.getFirstMatch(
                                      /rim\stablet\sos\s(\d+(\.\d+)*)/i,
                                      e
                                    ) ||
                                    o.default.getFirstMatch(
                                      /blackberry\d+\/(\d+([_\s]\d+)*)/i,
                                      e
                                    ) ||
                                    o.default.getFirstMatch(/\bbb(\d+)/i, e);
                                  return {
                                    name: i.OS_MAP.BlackBerry,
                                    version: t,
                                  };
                                },
                              },
                              {
                                test: [/bada/i],
                                describe: function (e) {
                                  var t = o.default.getFirstMatch(
                                    /bada\/(\d+(\.\d+)*)/i,
                                    e
                                  );
                                  return { name: i.OS_MAP.Bada, version: t };
                                },
                              },
                              {
                                test: [/tizen/i],
                                describe: function (e) {
                                  var t = o.default.getFirstMatch(
                                    /tizen[/\s](\d+(\.\d+)*)/i,
                                    e
                                  );
                                  return { name: i.OS_MAP.Tizen, version: t };
                                },
                              },
                              {
                                test: [/linux/i],
                                describe: function () {
                                  return { name: i.OS_MAP.Linux };
                                },
                              },
                              {
                                test: [/CrOS/],
                                describe: function () {
                                  return { name: i.OS_MAP.ChromeOS };
                                },
                              },
                              {
                                test: [/PlayStation 4/],
                                describe: function (e) {
                                  var t = o.default.getFirstMatch(
                                    /PlayStation 4[/\s](\d+(\.\d+)*)/i,
                                    e
                                  );
                                  return {
                                    name: i.OS_MAP.PlayStation4,
                                    version: t,
                                  };
                                },
                              },
                            ];
                          (t.default = a), (e.exports = t.default);
                        },
                        94: function (e, t, n) {
                          "use strict";
                          (t.__esModule = !0), (t.default = void 0);
                          var r,
                            o =
                              (r = n(17)) && r.__esModule ? r : { default: r },
                            i = n(18),
                            a = [
                              {
                                test: [/googlebot/i],
                                describe: function () {
                                  return { type: "bot", vendor: "Google" };
                                },
                              },
                              {
                                test: [/huawei/i],
                                describe: function (e) {
                                  var t =
                                      o.default.getFirstMatch(
                                        /(can-l01)/i,
                                        e
                                      ) && "Nova",
                                    n = {
                                      type: i.PLATFORMS_MAP.mobile,
                                      vendor: "Huawei",
                                    };
                                  return t && (n.model = t), n;
                                },
                              },
                              {
                                test: [/nexus\s*(?:7|8|9|10).*/i],
                                describe: function () {
                                  return {
                                    type: i.PLATFORMS_MAP.tablet,
                                    vendor: "Nexus",
                                  };
                                },
                              },
                              {
                                test: [/ipad/i],
                                describe: function () {
                                  return {
                                    type: i.PLATFORMS_MAP.tablet,
                                    vendor: "Apple",
                                    model: "iPad",
                                  };
                                },
                              },
                              {
                                test: [/Macintosh(.*?) FxiOS(.*?)\//],
                                describe: function () {
                                  return {
                                    type: i.PLATFORMS_MAP.tablet,
                                    vendor: "Apple",
                                    model: "iPad",
                                  };
                                },
                              },
                              {
                                test: [/kftt build/i],
                                describe: function () {
                                  return {
                                    type: i.PLATFORMS_MAP.tablet,
                                    vendor: "Amazon",
                                    model: "Kindle Fire HD 7",
                                  };
                                },
                              },
                              {
                                test: [/silk/i],
                                describe: function () {
                                  return {
                                    type: i.PLATFORMS_MAP.tablet,
                                    vendor: "Amazon",
                                  };
                                },
                              },
                              {
                                test: [/tablet(?! pc)/i],
                                describe: function () {
                                  return { type: i.PLATFORMS_MAP.tablet };
                                },
                              },
                              {
                                test: function (e) {
                                  var t = e.test(/ipod|iphone/i),
                                    n = e.test(/like (ipod|iphone)/i);
                                  return t && !n;
                                },
                                describe: function (e) {
                                  var t = o.default.getFirstMatch(
                                    /(ipod|iphone)/i,
                                    e
                                  );
                                  return {
                                    type: i.PLATFORMS_MAP.mobile,
                                    vendor: "Apple",
                                    model: t,
                                  };
                                },
                              },
                              {
                                test: [/nexus\s*[0-6].*/i, /galaxy nexus/i],
                                describe: function () {
                                  return {
                                    type: i.PLATFORMS_MAP.mobile,
                                    vendor: "Nexus",
                                  };
                                },
                              },
                              {
                                test: [/[^-]mobi/i],
                                describe: function () {
                                  return { type: i.PLATFORMS_MAP.mobile };
                                },
                              },
                              {
                                test: function (e) {
                                  return "blackberry" === e.getBrowserName(!0);
                                },
                                describe: function () {
                                  return {
                                    type: i.PLATFORMS_MAP.mobile,
                                    vendor: "BlackBerry",
                                  };
                                },
                              },
                              {
                                test: function (e) {
                                  return "bada" === e.getBrowserName(!0);
                                },
                                describe: function () {
                                  return { type: i.PLATFORMS_MAP.mobile };
                                },
                              },
                              {
                                test: function (e) {
                                  return "windows phone" === e.getBrowserName();
                                },
                                describe: function () {
                                  return {
                                    type: i.PLATFORMS_MAP.mobile,
                                    vendor: "Microsoft",
                                  };
                                },
                              },
                              {
                                test: function (e) {
                                  var t = Number(
                                    String(e.getOSVersion()).split(".")[0]
                                  );
                                  return (
                                    "android" === e.getOSName(!0) && t >= 3
                                  );
                                },
                                describe: function () {
                                  return { type: i.PLATFORMS_MAP.tablet };
                                },
                              },
                              {
                                test: function (e) {
                                  return "android" === e.getOSName(!0);
                                },
                                describe: function () {
                                  return { type: i.PLATFORMS_MAP.mobile };
                                },
                              },
                              {
                                test: function (e) {
                                  return "macos" === e.getOSName(!0);
                                },
                                describe: function () {
                                  return {
                                    type: i.PLATFORMS_MAP.desktop,
                                    vendor: "Apple",
                                  };
                                },
                              },
                              {
                                test: function (e) {
                                  return "windows" === e.getOSName(!0);
                                },
                                describe: function () {
                                  return { type: i.PLATFORMS_MAP.desktop };
                                },
                              },
                              {
                                test: function (e) {
                                  return "linux" === e.getOSName(!0);
                                },
                                describe: function () {
                                  return { type: i.PLATFORMS_MAP.desktop };
                                },
                              },
                              {
                                test: function (e) {
                                  return "playstation 4" === e.getOSName(!0);
                                },
                                describe: function () {
                                  return { type: i.PLATFORMS_MAP.tv };
                                },
                              },
                              {
                                test: function (e) {
                                  return "roku" === e.getOSName(!0);
                                },
                                describe: function () {
                                  return { type: i.PLATFORMS_MAP.tv };
                                },
                              },
                            ];
                          (t.default = a), (e.exports = t.default);
                        },
                        95: function (e, t, n) {
                          "use strict";
                          (t.__esModule = !0), (t.default = void 0);
                          var r,
                            o =
                              (r = n(17)) && r.__esModule ? r : { default: r },
                            i = n(18),
                            a = [
                              {
                                test: function (e) {
                                  return (
                                    "microsoft edge" === e.getBrowserName(!0)
                                  );
                                },
                                describe: function (e) {
                                  if (/\sedg\//i.test(e))
                                    return { name: i.ENGINE_MAP.Blink };
                                  var t = o.default.getFirstMatch(
                                    /edge\/(\d+(\.?_?\d+)+)/i,
                                    e
                                  );
                                  return {
                                    name: i.ENGINE_MAP.EdgeHTML,
                                    version: t,
                                  };
                                },
                              },
                              {
                                test: [/trident/i],
                                describe: function (e) {
                                  var t = { name: i.ENGINE_MAP.Trident },
                                    n = o.default.getFirstMatch(
                                      /trident\/(\d+(\.?_?\d+)+)/i,
                                      e
                                    );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: function (e) {
                                  return e.test(/presto/i);
                                },
                                describe: function (e) {
                                  var t = { name: i.ENGINE_MAP.Presto },
                                    n = o.default.getFirstMatch(
                                      /presto\/(\d+(\.?_?\d+)+)/i,
                                      e
                                    );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: function (e) {
                                  var t = e.test(/gecko/i),
                                    n = e.test(/like gecko/i);
                                  return t && !n;
                                },
                                describe: function (e) {
                                  var t = { name: i.ENGINE_MAP.Gecko },
                                    n = o.default.getFirstMatch(
                                      /gecko\/(\d+(\.?_?\d+)+)/i,
                                      e
                                    );
                                  return n && (t.version = n), t;
                                },
                              },
                              {
                                test: [/(apple)?webkit\/537\.36/i],
                                describe: function () {
                                  return { name: i.ENGINE_MAP.Blink };
                                },
                              },
                              {
                                test: [/(apple)?webkit/i],
                                describe: function (e) {
                                  var t = { name: i.ENGINE_MAP.WebKit },
                                    n = o.default.getFirstMatch(
                                      /webkit\/(\d+(\.?_?\d+)+)/i,
                                      e
                                    );
                                  return n && (t.version = n), t;
                                },
                              },
                            ];
                          (t.default = a), (e.exports = t.default);
                        },
                      });
                    },
                    156: function (t) {
                      "use strict";
                      t.exports = e;
                    },
                    486: function (e) {
                      "use strict";
                      e.exports = JSON.parse(
                        '{"name":"axios","version":"0.21.4","description":"Promise based HTTP client for the browser and node.js","main":"index.js","scripts":{"test":"grunt test","start":"node ./sandbox/server.js","build":"NODE_ENV=production grunt build","preversion":"npm test","version":"npm run build && grunt version && git add -A dist && git add CHANGELOG.md bower.json package.json","postversion":"git push && git push --tags","examples":"node ./examples/server.js","coveralls":"cat coverage/lcov.info | ./node_modules/coveralls/bin/coveralls.js","fix":"eslint --fix lib/**/*.js"},"repository":{"type":"git","url":"https://github.com/axios/axios.git"},"keywords":["xhr","http","ajax","promise","node"],"author":"Matt Zabriskie","license":"MIT","bugs":{"url":"https://github.com/axios/axios/issues"},"homepage":"https://axios-http.com","devDependencies":{"coveralls":"^3.0.0","es6-promise":"^4.2.4","grunt":"^1.3.0","grunt-banner":"^0.6.0","grunt-cli":"^1.2.0","grunt-contrib-clean":"^1.1.0","grunt-contrib-watch":"^1.0.0","grunt-eslint":"^23.0.0","grunt-karma":"^4.0.0","grunt-mocha-test":"^0.13.3","grunt-ts":"^6.0.0-beta.19","grunt-webpack":"^4.0.2","istanbul-instrumenter-loader":"^1.0.0","jasmine-core":"^2.4.1","karma":"^6.3.2","karma-chrome-launcher":"^3.1.0","karma-firefox-launcher":"^2.1.0","karma-jasmine":"^1.1.1","karma-jasmine-ajax":"^0.1.13","karma-safari-launcher":"^1.0.0","karma-sauce-launcher":"^4.3.6","karma-sinon":"^1.0.5","karma-sourcemap-loader":"^0.3.8","karma-webpack":"^4.0.2","load-grunt-tasks":"^3.5.2","minimist":"^1.2.0","mocha":"^8.2.1","sinon":"^4.5.0","terser-webpack-plugin":"^4.2.3","typescript":"^4.0.5","url-search-params":"^0.10.0","webpack":"^4.44.2","webpack-dev-server":"^3.11.0"},"browser":{"./lib/adapters/http.js":"./lib/adapters/xhr.js"},"jsdelivr":"dist/axios.min.js","unpkg":"dist/axios.min.js","typings":"./index.d.ts","dependencies":{"follow-redirects":"^1.14.0"},"bundlesize":[{"path":"./dist/axios.min.js","threshold":"5kB"}]}'
                      );
                    },
                  },
                  n = {};
                function r(e) {
                  var o = n[e];
                  if (void 0 !== o) return o.exports;
                  var i = (n[e] = { exports: {} });
                  return t[e].call(i.exports, i, i.exports, r), i.exports;
                }
                (r.n = function (e) {
                  var t =
                    e && e.__esModule
                      ? function () {
                          return e.default;
                        }
                      : function () {
                          return e;
                        };
                  return r.d(t, { a: t }), t;
                }),
                  (r.d = function (e, t) {
                    for (var n in t)
                      r.o(t, n) &&
                        !r.o(e, n) &&
                        Object.defineProperty(e, n, {
                          enumerable: !0,
                          get: t[n],
                        });
                  }),
                  (r.o = function (e, t) {
                    return Object.prototype.hasOwnProperty.call(e, t);
                  }),
                  (r.r = function (e) {
                    "undefined" != typeof Symbol &&
                      Symbol.toStringTag &&
                      Object.defineProperty(e, Symbol.toStringTag, {
                        value: "Module",
                      }),
                      Object.defineProperty(e, "__esModule", { value: !0 });
                  });
                var o = {};
                return (
                  (function () {
                    "use strict";
                    r.r(o),
                      r.d(o, {
                        AGENT_STATUS: function () {
                          return Z;
                        },
                        CONNECTION_STATUS: function () {
                          return U;
                        },
                        ErrorBoundary: function () {
                          return C;
                        },
                        MephistoContext: function () {
                          return A;
                        },
                        STATUS_TO_TEXT_MAP: function () {
                          return J;
                        },
                        axiosInstance: function () {
                          return b;
                        },
                        doesSupportWebsockets: function () {
                          return w;
                        },
                        getBlockedExplanation: function () {
                          return P;
                        },
                        getTaskConfig: function () {
                          return x;
                        },
                        isMobile: function () {
                          return v;
                        },
                        libVersion: function () {
                          return M;
                        },
                        postCompleteOnboarding: function () {
                          return _;
                        },
                        postCompleteTask: function () {
                          return S;
                        },
                        postData: function () {
                          return g;
                        },
                        postErrorLog: function () {
                          return O;
                        },
                        postMetadata: function () {
                          return T;
                        },
                        postProviderRequest: function () {
                          return k;
                        },
                        pythonTime: function () {
                          return N;
                        },
                        requestAgent: function () {
                          return E;
                        },
                        useMephistoLiveTask: function () {
                          return ee;
                        },
                        useMephistoRemoteProcedureTask: function () {
                          return ae;
                        },
                        useMephistoSocket: function () {
                          return q;
                        },
                        useMephistoTask: function () {
                          return fe;
                        },
                      });
                    var e = r(156),
                      t = r.n(e),
                      n = r(393),
                      i = r.n(n);
                    function a(e) {
                      return (
                        (a =
                          "function" == typeof Symbol &&
                          "symbol" == l(Symbol.iterator)
                            ? function (e) {
                                return l(e);
                              }
                            : function (e) {
                                return e &&
                                  "function" == typeof Symbol &&
                                  e.constructor === Symbol &&
                                  e !== Symbol.prototype
                                  ? "symbol"
                                  : l(e);
                              }),
                        a(e)
                      );
                    }
                    function s(e, t) {
                      if (!(e instanceof t))
                        throw new TypeError(
                          "Cannot call a class as a function"
                        );
                    }
                    function u(e, t) {
                      return (
                        (u = Object.setPrototypeOf
                          ? Object.setPrototypeOf.bind()
                          : function (e, t) {
                              return (e.__proto__ = t), e;
                            }),
                        u(e, t)
                      );
                    }
                    function c(e, t) {
                      if (t && ("object" === a(t) || "function" == typeof t))
                        return t;
                      if (void 0 !== t)
                        throw new TypeError(
                          "Derived constructors may only return object or undefined"
                        );
                      return f(e);
                    }
                    function f(e) {
                      if (void 0 === e)
                        throw new ReferenceError(
                          "this hasn't been initialised - super() hasn't been called"
                        );
                      return e;
                    }
                    function d(e) {
                      return (
                        (d = Object.setPrototypeOf
                          ? Object.getPrototypeOf.bind()
                          : function (e) {
                              return e.__proto__ || Object.getPrototypeOf(e);
                            }),
                        d(e)
                      );
                    }
                    function p(e, t) {
                      var n = Object.keys(e);
                      if (Object.getOwnPropertySymbols) {
                        var r = Object.getOwnPropertySymbols(e);
                        t &&
                          (r = r.filter(function (t) {
                            return Object.getOwnPropertyDescriptor(
                              e,
                              t
                            ).enumerable;
                          })),
                          n.push.apply(n, r);
                      }
                      return n;
                    }
                    function m(e) {
                      for (var t = 1; t < arguments.length; t++) {
                        var n = null != arguments[t] ? arguments[t] : {};
                        t % 2
                          ? p(Object(n), !0).forEach(function (t) {
                              h(e, t, n[t]);
                            })
                          : Object.getOwnPropertyDescriptors
                          ? Object.defineProperties(
                              e,
                              Object.getOwnPropertyDescriptors(n)
                            )
                          : p(Object(n)).forEach(function (t) {
                              Object.defineProperty(
                                e,
                                t,
                                Object.getOwnPropertyDescriptor(n, t)
                              );
                            });
                      }
                      return e;
                    }
                    function h(e, t, n) {
                      return (
                        t in e
                          ? Object.defineProperty(e, t, {
                              value: n,
                              enumerable: !0,
                              configurable: !0,
                              writable: !0,
                            })
                          : (e[t] = n),
                        e
                      );
                    }
                    var b = r(285).create();
                    function g() {
                      var e =
                          arguments.length > 0 && void 0 !== arguments[0]
                            ? arguments[0]
                            : "",
                        t =
                          arguments.length > 1 && void 0 !== arguments[1]
                            ? arguments[1]
                            : {};
                      return b({
                        url: e,
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        data: t,
                      }).then(function (e) {
                        return e.data;
                      });
                    }
                    function v() {
                      return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
                        navigator.userAgent
                      );
                    }
                    b.interceptors.request.use(function (e) {
                      var t = (function () {
                        try {
                          return getProviderURLParams
                            ? "function" == typeof getProviderURLParams
                              ? getProviderURLParams()
                              : getProviderURLParams
                            : null;
                        } catch (e) {
                          if (e instanceof ReferenceError) return null;
                          throw e;
                        }
                      })();
                      return t ? ((e.params = m(m({}, e.params), t)), e) : e;
                    });
                    var y = i().getParser(window.navigator.userAgent);
                    function w() {
                      return y.satisfies({
                        "internet explorer": ">=10",
                        chrome: ">=16",
                        firefox: ">=11",
                        opera: ">=12.1",
                        safari: ">=7",
                        "android browser": ">=3",
                      });
                    }
                    function x() {
                      return b("/task_config.json", {
                        params: { mephisto_task_version: M },
                      }).then(function (e) {
                        var t = e.data;
                        return (
                          t.mephisto_task_version !== M &&
                            console.warn(
                              "Version mismatch detected! Local `mephisto-task` package is on version " +
                                M +
                                " but the server expected version " +
                                t.mephisto_task_version +
                                ". Please ensure you are using the package version expected by the Mephisto backend."
                            ),
                          e.data
                        );
                      });
                    }
                    function k(e, t) {
                      return g(new URL(window.location.origin + e).toString(), {
                        provider_data: t,
                        client_timestamp: N(),
                      });
                    }
                    function E() {
                      return k("/request_agent", getAgentRegistration());
                    }
                    function _(e, t) {
                      return k("/submit_onboarding", {
                        USED_AGENT_ID: e,
                        onboarding_data: t,
                      });
                    }
                    function S(e, t) {
                      return g("/submit_task", {
                        USED_AGENT_ID: e,
                        final_data: t,
                        client_timestamp: N(),
                      })
                        .then(function (e) {
                          return handleSubmitToProvider(t), e;
                        })
                        .then(function (e) {
                          console.log("Submitted");
                        });
                    }
                    function T(e, t) {
                      return g("/submit_metadata", {
                        USED_AGENT_ID: e,
                        metadata: t,
                        client_timestamp: N(),
                      }).then(function (e) {
                        return e;
                      });
                    }
                    function O(e, t) {
                      return g("/log_error", {
                        USED_AGENT_ID: e,
                        error_data: t,
                        client_timestamp: N(),
                      }).then(function (e) {});
                    }
                    function P(e) {
                      var t = {
                        no_mobile:
                          "Sorry, this task cannot be completed on mobile devices. Please use a computer.",
                        no_websockets:
                          "Sorry, your browser does not support the required version of websockets for this task. Please upgrade to a modern browser.",
                      };
                      return e in t
                        ? t[e]
                        : "Sorry, you are not able to work on this task. (code: ".concat(
                            e,
                            ")"
                          );
                    }
                    var C = (function (e) {
                        !(function (e, t) {
                          if ("function" != typeof t && null !== t)
                            throw new TypeError(
                              "Super expression must either be null or a function"
                            );
                          (e.prototype = Object.create(t && t.prototype, {
                            constructor: {
                              value: e,
                              writable: !0,
                              configurable: !0,
                            },
                          })),
                            Object.defineProperty(e, "prototype", {
                              writable: !1,
                            }),
                            t && u(e, t);
                        })(l, e);
                        var n,
                          r,
                          o,
                          i,
                          a =
                            ((o = l),
                            (i = (function () {
                              if (
                                "undefined" == typeof Reflect ||
                                !Reflect.construct
                              )
                                return !1;
                              if (Reflect.construct.sham) return !1;
                              if ("function" == typeof Proxy) return !0;
                              try {
                                return (
                                  Boolean.prototype.valueOf.call(
                                    Reflect.construct(
                                      Boolean,
                                      [],
                                      function () {}
                                    )
                                  ),
                                  !0
                                );
                              } catch (e) {
                                return !1;
                              }
                            })()),
                            function () {
                              var e,
                                t = d(o);
                              if (i) {
                                var n = d(this).constructor;
                                e = Reflect.construct(t, arguments, n);
                              } else e = t.apply(this, arguments);
                              return c(this, e);
                            });
                        function l() {
                          var e;
                          s(this, l);
                          for (
                            var t = arguments.length, n = new Array(t), r = 0;
                            r < t;
                            r++
                          )
                            n[r] = arguments[r];
                          return (
                            h(
                              f((e = a.call.apply(a, [this].concat(n)))),
                              "state",
                              { error: null, errorInfo: null }
                            ),
                            e
                          );
                        }
                        return (
                          (n = l),
                          (r = [
                            {
                              key: "componentDidCatch",
                              value: function (e, t) {
                                this.setState({ error: e, errorInfo: t }),
                                  this.props.handleError &&
                                    this.props.handleError({
                                      error: e.message,
                                      errorInfo: t,
                                    });
                              },
                            },
                            {
                              key: "render",
                              value: function () {
                                return this.state.errorInfo
                                  ? t().createElement(
                                      "div",
                                      null,
                                      t().createElement(
                                        "h2",
                                        null,
                                        "Oops! Something went wrong."
                                      ),
                                      t().createElement(
                                        "details",
                                        { style: { whiteSpace: "pre-wrap" } },
                                        this.state.error &&
                                          this.state.error.toString(),
                                        t().createElement("br", null),
                                        this.state.errorInfo.componentStack
                                      )
                                    )
                                  : this.props.children;
                              },
                            },
                          ]) &&
                            (function (e, t) {
                              for (var n = 0; n < t.length; n++) {
                                var r = t[n];
                                (r.enumerable = r.enumerable || !1),
                                  (r.configurable = !0),
                                  "value" in r && (r.writable = !0),
                                  Object.defineProperty(e, r.key, r);
                              }
                            })(n.prototype, r),
                          Object.defineProperty(n, "prototype", {
                            writable: !1,
                          }),
                          l
                        );
                      })(t().Component),
                      M = "2.0.2";
                    function N() {
                      return Date.now() / 1e3;
                    }
                    var A = t().createContext({});
                    function j(e, t) {
                      var n = Object.keys(e);
                      if (Object.getOwnPropertySymbols) {
                        var r = Object.getOwnPropertySymbols(e);
                        t &&
                          (r = r.filter(function (t) {
                            return Object.getOwnPropertyDescriptor(
                              e,
                              t
                            ).enumerable;
                          })),
                          n.push.apply(n, r);
                      }
                      return n;
                    }
                    function R(e) {
                      for (var t = 1; t < arguments.length; t++) {
                        var n = null != arguments[t] ? arguments[t] : {};
                        t % 2
                          ? j(Object(n), !0).forEach(function (t) {
                              F(e, t, n[t]);
                            })
                          : Object.getOwnPropertyDescriptors
                          ? Object.defineProperties(
                              e,
                              Object.getOwnPropertyDescriptors(n)
                            )
                          : j(Object(n)).forEach(function (t) {
                              Object.defineProperty(
                                e,
                                t,
                                Object.getOwnPropertyDescriptor(n, t)
                              );
                            });
                      }
                      return e;
                    }
                    function F(e, t, n) {
                      return (
                        t in e
                          ? Object.defineProperty(e, t, {
                              value: n,
                              enumerable: !0,
                              configurable: !0,
                              writable: !0,
                            })
                          : (e[t] = n),
                        e
                      );
                    }
                    function I(e, t) {
                      return (
                        (function (e) {
                          if (Array.isArray(e)) return e;
                        })(e) ||
                        (function (e, t) {
                          var n =
                            null == e
                              ? null
                              : ("undefined" != typeof Symbol &&
                                  e[Symbol.iterator]) ||
                                e["@@iterator"];
                          if (null != n) {
                            var r,
                              o,
                              i = [],
                              a = !0,
                              l = !1;
                            try {
                              for (
                                n = n.call(e);
                                !(a = (r = n.next()).done) &&
                                (i.push(r.value), !t || i.length !== t);
                                a = !0
                              );
                            } catch (e) {
                              (l = !0), (o = e);
                            } finally {
                              try {
                                a || null == n.return || n.return();
                              } finally {
                                if (l) throw o;
                              }
                            }
                            return i;
                          }
                        })(e, t) ||
                        L(e, t) ||
                        (function () {
                          throw new TypeError(
                            "Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."
                          );
                        })()
                      );
                    }
                    function L(e, t) {
                      if (e) {
                        if ("string" == typeof e) return z(e, t);
                        var n = Object.prototype.toString.call(e).slice(8, -1);
                        return (
                          "Object" === n &&
                            e.constructor &&
                            (n = e.constructor.name),
                          "Map" === n || "Set" === n
                            ? Array.from(e)
                            : "Arguments" === n ||
                              /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)
                            ? z(e, t)
                            : void 0
                        );
                      }
                    }
                    function z(e, t) {
                      (null == t || t > e.length) && (t = e.length);
                      for (var n = 0, r = new Array(t); n < t; n++) r[n] = e[n];
                      return r;
                    }
                    var D,
                      B = "heartbeat",
                      U = {
                        FAILED: "failed",
                        INITIALIZING: "initializing",
                        WEBSOCKETS_FAILURE: "websockets_failure",
                        CONNECTED: "connected",
                        DISCONNECTED: "disconnected",
                        RECONNECTING_ROUTER: "reconnecting_router",
                        DISCONNECTED_ROUTER: "disconnected_router",
                        RECONNECTING_SERVER: "reconnecting_server",
                        DISCONNECTED_SERVER: "disconnected_server",
                      },
                      W = (function () {
                        function e() {
                          !(function (e, t) {
                            if (!(e instanceof t))
                              throw new TypeError(
                                "Cannot call a class as a function"
                              );
                          })(this, e),
                            (this.data = []);
                        }
                        var t, n;
                        return (
                          (t = e),
                          (n = [
                            {
                              key: "push",
                              value: function (e, t) {
                                t = +t;
                                for (
                                  var n = 0;
                                  n < this.data.length && this.data[n][0] < t;
                                  n++
                                );
                                this.data.splice(n, 0, [e, t]);
                              },
                            },
                            {
                              key: "pop",
                              value: function () {
                                return this.data.shift();
                              },
                            },
                            {
                              key: "peek",
                              value: function () {
                                return this.data[0];
                              },
                            },
                            {
                              key: "size",
                              value: function () {
                                return this.data.length;
                              },
                            },
                          ]) &&
                            (function (e, t) {
                              for (var n = 0; n < t.length; n++) {
                                var r = t[n];
                                (r.enumerable = r.enumerable || !1),
                                  (r.configurable = !0),
                                  "value" in r && (r.writable = !0),
                                  Object.defineProperty(e, r.key, r);
                              }
                            })(t.prototype, n),
                          Object.defineProperty(t, "prototype", {
                            writable: !1,
                          }),
                          e
                        );
                      })();
                    function V(e, t) {
                      4 >= t && console.log(e);
                    }
                    function H(e, t) {
                      return null == e ? t : e;
                    }
                    function q(e) {
                      var n = e.onConnectionStatusChange,
                        r = e.onLiveUpdate,
                        o = e.onStatusUpdate,
                        i = e.config,
                        a = void 0 === i ? {} : i,
                        l = {
                          heartbeat_id: null,
                          socket_terminated: !1,
                          setting_socket: !1,
                          heartbeats_without_response: 0,
                          last_mephisto_ping: Date.now(),
                          used_update_ids: [],
                        },
                        s = t().useReducer(function (e, t) {
                          return R(R({}, e), t);
                        }, l),
                        u = I(s, 2),
                        c = u[0],
                        f = u[1],
                        d = t().useRef(),
                        p = t().useRef(new W()),
                        m = t().useRef();
                      function h() {
                        if (
                          !c.socket_terminated &&
                          p.current.size() > 0 &&
                          Date.now() > p.current.peek()[1]
                        ) {
                          var e = I(p.current.pop(), 2),
                            t = e[0],
                            n = e[1];
                          b(t) || p.current.push(t, n);
                        }
                      }
                      function b(e) {
                        if (0 == d.current.readyState) return !1;
                        if (d.current.readyState > 1)
                          return (
                            V(
                              "Socket not in ready state, restarting if possible",
                              2
                            ),
                            g(),
                            !1
                          );
                        try {
                          return (
                            d.current.send(JSON.stringify(e.packet)),
                            void 0 !== e.callback && e.callback(e.packet),
                            !0
                          );
                        } catch (e) {
                          return g(), !1;
                        }
                      }
                      function g() {
                        setTimeout(function () {
                          try {
                            d.current.close();
                          } catch (e) {
                            V(
                              "Server had error " +
                                e +
                                " when closing after an error",
                              1
                            );
                          }
                          m.current.setupWebsocket();
                        }, 0);
                      }
                      function v(e, t, n) {
                        var r = Date.now();
                        void 0 === t.update_id &&
                          (t.update_id = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(
                            /[xy]/g,
                            function (e) {
                              var t = (16 * Math.random()) | 0;
                              return ("x" == e ? t : (3 & t) | 8).toString(16);
                            }
                          ));
                        var o = {
                          packet: {
                            packet_type: e,
                            subject_id: c.agentId,
                            data: t,
                            client_timestamp: N(),
                          },
                          callback: n,
                        };
                        p.current.push(o, r);
                      }
                      function y() {
                        if (!c.setting_socket && !c.socket_terminated) {
                          f({ setting_socket: !0 }),
                            window.setTimeout(function () {
                              return f({ setting_socket: !1 });
                            }, 4e3);
                          var e = window.location,
                            t =
                              ("https:" == e.protocol ? "wss://" : "ws://") +
                              e.hostname +
                              ":" +
                              e.port;
                          (d.current = new WebSocket(t)),
                            (d.current.onmessage = function (e) {
                              !(function (e) {
                                if (
                                  "client_bound_live_update" == e.packet_type
                                ) {
                                  var t = c.used_update_ids;
                                  if (t.includes(e.data.update_id))
                                    return void V(
                                      "Skipping existing update_id " +
                                        e.data.update_id,
                                      3
                                    );
                                  var n = [].concat(
                                    (function (e) {
                                      if (Array.isArray(e)) return z(e);
                                    })((i = t)) ||
                                      (function (e) {
                                        if (
                                          ("undefined" != typeof Symbol &&
                                            null != e[Symbol.iterator]) ||
                                          null != e["@@iterator"]
                                        )
                                          return Array.from(e);
                                      })(i) ||
                                      L(i) ||
                                      (function () {
                                        throw new TypeError(
                                          "Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."
                                        );
                                      })(),
                                    [e.data.update_id]
                                  );
                                  f({ used_update_ids: n }), r(e.data);
                                } else
                                  "update_status" == e.packet_type
                                    ? o(e.data)
                                    : e.packet_type == B &&
                                      f({
                                        last_mephisto_ping:
                                          e.data.last_mephisto_ping,
                                        heartbeats_without_response: 0,
                                      });
                                var i;
                              })(JSON.parse(e.data));
                            }),
                            (d.current.onopen = function () {
                              if (
                                (V("Server connected.", 2),
                                m.current.enqueuePacket(
                                  "alive",
                                  {},
                                  function () {
                                    n(U.CONNECTED);
                                  }
                                ),
                                window.setTimeout(function () {
                                  1 === d.current.readyState ||
                                    c.socket_terminated ||
                                    n(U.FAILED);
                                }, 1e4),
                                window.setTimeout(function () {
                                  return m.current.sendHeartbeat();
                                }, 500),
                                null == c.heartbeat_id)
                              ) {
                                var e = window.setInterval(function () {
                                  return m.current.heartbeatThread();
                                }, H(a.heartbeatTime, 6e3));
                                f({ heartbeat_id: e });
                              }
                              f({ setting_socket: !1 });
                            }),
                            (d.current.onerror = function (e) {
                              console.error(e), g();
                            }),
                            (d.current.onclose = function () {
                              V("Server closing.", 3), n(U.DISCONNECTED);
                            });
                        }
                      }
                      function w() {
                        return c.socket_terminated
                          ? (window.clearInterval(c.heartbeat_id),
                            void f({ heartbeat_id: null }))
                          : (c.heartbeats_without_response ===
                              H(a.refreshSocketMissedResponses, 5) &&
                              (n(U.RECONNECTING_ROUTER), g()),
                            c.heartbeats_without_response >=
                              H(a.routerDeadTimeout, 10) &&
                              (n(U.DISCONNECTED_ROUTER),
                              m.current.closeSocket()),
                            Date.now() - c.last_mephisto_ping >
                            H(a.connectionDeadMephistoPing, 2e4)
                              ? (m.current.closeSocket(),
                                o({ status: "mephisto disconnect" }),
                                n(U.DISCONNECTED_SERVER),
                                window.clearInterval(c.heartbeat_id),
                                void f({ heartbeat_id: null }))
                              : void m.current.sendHeartbeat());
                      }
                      function x() {
                        b({
                          packet: {
                            packet_type: B,
                            subject_id: c.agentId,
                            client_timestamp: N(),
                          },
                        }),
                          f({
                            heartbeats_without_response:
                              c.heartbeats_without_response + 1,
                          });
                      }
                      function k() {
                        c.socket_terminated
                          ? V("Socket already closed", 2)
                          : (V("Socket closing", 3),
                            d.current.close(),
                            f({ socket_terminated: !0 }));
                      }
                      return (
                        t().useEffect(function () {
                          m.current = {
                            sendingThread: h,
                            heartbeatThread: w,
                            closeSocket: k,
                            setupWebsocket: y,
                            enqueuePacket: v,
                            sendHeartbeat: x,
                          };
                        }),
                        {
                          connect: function (e) {
                            n(U.INITIALIZING),
                              m.current.setupWebsocket(),
                              m.current.sendingThread();
                            var t = window.setInterval(function () {
                              return m.current.sendingThread();
                            }, H(a.sendThreadRefresh, 100));
                            f({ agentId: e, messageSenderThreadId: t });
                          },
                          destroy: function () {
                            return m.current.closeSocket();
                          },
                          sendLiveUpdate: function (e) {
                            return new Promise(function (t) {
                              m.current.enqueuePacket(
                                "mephisto_bound_live_update",
                                e,
                                function (e) {
                                  t(e.data);
                                }
                              );
                            });
                          },
                        }
                      );
                    }
                    function Q(e, t) {
                      var n = Object.keys(e);
                      if (Object.getOwnPropertySymbols) {
                        var r = Object.getOwnPropertySymbols(e);
                        t &&
                          (r = r.filter(function (t) {
                            return Object.getOwnPropertyDescriptor(
                              e,
                              t
                            ).enumerable;
                          })),
                          n.push.apply(n, r);
                      }
                      return n;
                    }
                    function K(e) {
                      for (var t = 1; t < arguments.length; t++) {
                        var n = null != arguments[t] ? arguments[t] : {};
                        t % 2
                          ? Q(Object(n), !0).forEach(function (t) {
                              X(e, t, n[t]);
                            })
                          : Object.getOwnPropertyDescriptors
                          ? Object.defineProperties(
                              e,
                              Object.getOwnPropertyDescriptors(n)
                            )
                          : Q(Object(n)).forEach(function (t) {
                              Object.defineProperty(
                                e,
                                t,
                                Object.getOwnPropertyDescriptor(n, t)
                              );
                            });
                      }
                      return e;
                    }
                    function G(e, t) {
                      return (
                        (function (e) {
                          if (Array.isArray(e)) return e;
                        })(e) ||
                        (function (e, t) {
                          var n =
                            null == e
                              ? null
                              : ("undefined" != typeof Symbol &&
                                  e[Symbol.iterator]) ||
                                e["@@iterator"];
                          if (null != n) {
                            var r,
                              o,
                              i = [],
                              a = !0,
                              l = !1;
                            try {
                              for (
                                n = n.call(e);
                                !(a = (r = n.next()).done) &&
                                (i.push(r.value), !t || i.length !== t);
                                a = !0
                              );
                            } catch (e) {
                              (l = !0), (o = e);
                            } finally {
                              try {
                                a || null == n.return || n.return();
                              } finally {
                                if (l) throw o;
                              }
                            }
                            return i;
                          }
                        })(e, t) ||
                        $(e, t) ||
                        (function () {
                          throw new TypeError(
                            "Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."
                          );
                        })()
                      );
                    }
                    function $(e, t) {
                      if (e) {
                        if ("string" == typeof e) return Y(e, t);
                        var n = Object.prototype.toString.call(e).slice(8, -1);
                        return (
                          "Object" === n &&
                            e.constructor &&
                            (n = e.constructor.name),
                          "Map" === n || "Set" === n
                            ? Array.from(e)
                            : "Arguments" === n ||
                              /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)
                            ? Y(e, t)
                            : void 0
                        );
                      }
                    }
                    function Y(e, t) {
                      (null == t || t > e.length) && (t = e.length);
                      for (var n = 0, r = new Array(t); n < t; n++) r[n] = e[n];
                      return r;
                    }
                    function X(e, t, n) {
                      return (
                        t in e
                          ? Object.defineProperty(e, t, {
                              value: n,
                              enumerable: !0,
                              configurable: !0,
                              writable: !0,
                            })
                          : (e[t] = n),
                        e
                      );
                    }
                    var Z = {
                        NONE: "none",
                        ONBOARDING: "onboarding",
                        WAITING: "waiting",
                        IN_TASK: "in task",
                        DONE: "done",
                        DISCONNECT: "disconnect",
                        TIMEOUT: "timeout",
                        PARTNER_DISCONNECT: "partner disconnect",
                        EXPIRED: "expired",
                        RETURNED: "returned",
                        MEPHISTO_DISCONNECT: "mephisto disconnect",
                      },
                      J =
                        (X(
                          (D = {}),
                          Z.EXPIRED,
                          "This task is no longer available to be completed.  Please return it and try a different task"
                        ),
                        X(
                          D,
                          Z.TIMEOUT,
                          "You took to long to respond to this task, and have timed out. The task is no longer available, please return it."
                        ),
                        X(
                          D,
                          Z.DISCONNECT,
                          "You have disconnected from our server during the duration of the task. If you have done substantial work, please reach out to see if we can recover it. "
                        ),
                        X(
                          D,
                          Z.RETURNED,
                          "You have disconnected from our server during the duration of the task. If you have done substantial work, please reach out to see if we can recover it. "
                        ),
                        X(
                          D,
                          Z.PARTNER_DISCONNECT,
                          "One of your partners has disconnected while working on this task. We won't penalize you for them leaving, so please submit this task as is."
                        ),
                        X(
                          D,
                          Z.MEPHISTO_DISCONNECT,
                          "Our server appears to have gone down during the duration of this Task. Please send us a message if you've done substantial work and we can find out if the task is complete enough to compensate."
                        ),
                        D),
                      ee = function (e) {
                        var n = G(t().useState(""), 2),
                          r = n[0],
                          o = n[1],
                          i = G(t().useState(null), 2),
                          a = i[0],
                          l = i[1],
                          s = q,
                          u = e.customConnectionHook || s,
                          c = fe(),
                          f = c.initialTaskData;
                        function d(t) {
                          e.onLiveUpdate && e.onLiveUpdate(t);
                        }
                        t().useEffect(
                          function () {
                            if (null != f && f.past_live_updates) {
                              var e,
                                t = (function (e, t) {
                                  var n =
                                    ("undefined" != typeof Symbol &&
                                      e[Symbol.iterator]) ||
                                    e["@@iterator"];
                                  if (!n) {
                                    if (Array.isArray(e) || (n = $(e))) {
                                      n && (e = n);
                                      var r = 0,
                                        o = function () {};
                                      return {
                                        s: o,
                                        n: function () {
                                          return r >= e.length
                                            ? { done: !0 }
                                            : { done: !1, value: e[r++] };
                                        },
                                        e: function (e) {
                                          throw e;
                                        },
                                        f: o,
                                      };
                                    }
                                    throw new TypeError(
                                      "Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."
                                    );
                                  }
                                  var i,
                                    a = !0,
                                    l = !1;
                                  return {
                                    s: function () {
                                      n = n.call(e);
                                    },
                                    n: function () {
                                      var e = n.next();
                                      return (a = e.done), e;
                                    },
                                    e: function (e) {
                                      (l = !0), (i = e);
                                    },
                                    f: function () {
                                      try {
                                        a || null == n.return || n.return();
                                      } finally {
                                        if (l) throw i;
                                      }
                                    },
                                  };
                                })(f.past_live_updates);
                              try {
                                for (t.s(); !(e = t.n()).done; ) d(e.value);
                              } catch (e) {
                                t.e(e);
                              } finally {
                                t.f();
                              }
                            }
                          },
                          [f]
                        );
                        var p = u({
                          onConnectionStatusChange: function (e) {
                            o(e);
                          },
                          onStatusUpdate: function (t) {
                            var n = t.status;
                            l(n),
                              e.onStatusUpdate &&
                                e.onStatusUpdate({ status: n });
                          },
                          onLiveUpdate: d,
                        });
                        return (
                          w() || (c.blockedReason = "no_websockets"),
                          K(
                            K(K({}, c), p),
                            {},
                            { connectionStatus: r, agentStatus: a }
                          )
                        );
                      },
                      te = ["connect", "destroy", "sendLiveUpdate"];
                    function ne(e, t) {
                      var n = Object.keys(e);
                      if (Object.getOwnPropertySymbols) {
                        var r = Object.getOwnPropertySymbols(e);
                        t &&
                          (r = r.filter(function (t) {
                            return Object.getOwnPropertyDescriptor(
                              e,
                              t
                            ).enumerable;
                          })),
                          n.push.apply(n, r);
                      }
                      return n;
                    }
                    function re(e) {
                      for (var t = 1; t < arguments.length; t++) {
                        var n = null != arguments[t] ? arguments[t] : {};
                        t % 2
                          ? ne(Object(n), !0).forEach(function (t) {
                              oe(e, t, n[t]);
                            })
                          : Object.getOwnPropertyDescriptors
                          ? Object.defineProperties(
                              e,
                              Object.getOwnPropertyDescriptors(n)
                            )
                          : ne(Object(n)).forEach(function (t) {
                              Object.defineProperty(
                                e,
                                t,
                                Object.getOwnPropertyDescriptor(n, t)
                              );
                            });
                      }
                      return e;
                    }
                    function oe(e, t, n) {
                      return (
                        t in e
                          ? Object.defineProperty(e, t, {
                              value: n,
                              enumerable: !0,
                              configurable: !0,
                              writable: !0,
                            })
                          : (e[t] = n),
                        e
                      );
                    }
                    function ie(e, t) {
                      (null == t || t > e.length) && (t = e.length);
                      for (var n = 0, r = new Array(t); n < t; n++) r[n] = e[n];
                      return r;
                    }
                    var ae = function (e) {
                      var n,
                        r =
                          (function (e) {
                            if (Array.isArray(e)) return e;
                          })((n = t().useState())) ||
                          (function (e, t) {
                            var n =
                              null == e
                                ? null
                                : ("undefined" != typeof Symbol &&
                                    e[Symbol.iterator]) ||
                                  e["@@iterator"];
                            if (null != n) {
                              var r,
                                o,
                                i = [],
                                a = !0,
                                l = !1;
                              try {
                                for (
                                  n = n.call(e);
                                  !(a = (r = n.next()).done) &&
                                  (i.push(r.value), 2 !== i.length);
                                  a = !0
                                );
                              } catch (e) {
                                (l = !0), (o = e);
                              } finally {
                                try {
                                  a || null == n.return || n.return();
                                } finally {
                                  if (l) throw o;
                                }
                              }
                              return i;
                            }
                          })(n) ||
                          (function (e, t) {
                            if (e) {
                              if ("string" == typeof e) return ie(e, 2);
                              var n = Object.prototype.toString
                                .call(e)
                                .slice(8, -1);
                              return (
                                "Object" === n &&
                                  e.constructor &&
                                  (n = e.constructor.name),
                                "Map" === n || "Set" === n
                                  ? Array.from(e)
                                  : "Arguments" === n ||
                                    /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(
                                      n
                                    )
                                  ? ie(e, 2)
                                  : void 0
                              );
                            }
                          })(n) ||
                          (function () {
                            throw new TypeError(
                              "Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."
                            );
                          })(),
                        o = r[0],
                        i = r[1],
                        a = t().useRef({}),
                        l = ee(
                          re(
                            {
                              onStatusUpdate: function (e) {
                                var t = e.status;
                                [
                                  Z.DISCONNECT,
                                  Z.RETURNED,
                                  Z.EXPIRED,
                                  Z.TIMEOUT,
                                  Z.MEPHISTO_DISCONNECT,
                                ].includes(t) && i(J[t]);
                              },
                              onLiveUpdate: function (e) {
                                !(function (e) {
                                  var t = a.current[e.handles];
                                  if (void 0 !== t) {
                                    var n = JSON.parse(e.response);
                                    t.callback(n);
                                  } else
                                    console.log(
                                      "No request found to handle this live update",
                                      e
                                    );
                                })(e);
                              },
                            },
                            e
                          )
                        ),
                        s = l.connect,
                        u = l.destroy,
                        c = l.sendLiveUpdate,
                        f = (function (e, t) {
                          if (null == e) return {};
                          var n,
                            r,
                            o = (function (e, t) {
                              if (null == e) return {};
                              var n,
                                r,
                                o = {},
                                i = Object.keys(e);
                              for (r = 0; r < i.length; r++)
                                (n = i[r]), t.indexOf(n) >= 0 || (o[n] = e[n]);
                              return o;
                            })(e, t);
                          if (Object.getOwnPropertySymbols) {
                            var i = Object.getOwnPropertySymbols(e);
                            for (r = 0; r < i.length; r++)
                              (n = i[r]),
                                t.indexOf(n) >= 0 ||
                                  (Object.prototype.propertyIsEnumerable.call(
                                    e,
                                    n
                                  ) &&
                                    (o[n] = e[n]));
                          }
                          return o;
                        })(l, te),
                        d = l.agentId,
                        p = { connect: s, destroy: u, sendLiveUpdate: c };
                      t().useEffect(
                        function () {
                          d && (console.log("connecting..."), s(d));
                        },
                        [d]
                      );
                      var m = t().useCallback(
                        function (e) {
                          var t = e.targetEvent,
                            n = e.args,
                            r = e.callback,
                            o = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(
                              /[xy]/g,
                              function (e) {
                                var t = (16 * Math.random()) | 0;
                                return ("x" == e ? t : (3 & t) | 8).toString(
                                  16
                                );
                              }
                            ),
                            i = {
                              request_id: o,
                              target: t,
                              args: JSON.stringify(n),
                            };
                          return (
                            c(i).then(function (e) {
                              void 0 !== r &&
                                ((e.callback = r),
                                (e.args = n),
                                (a.current[o] = e));
                            }),
                            o
                          );
                        },
                        [d]
                      );
                      return re(
                        re({}, f),
                        {},
                        {
                          remoteProcedure: function (e) {
                            var t = function (t) {
                              return new Promise(function (n, r) {
                                void 0 !== o
                                  ? r({ disconnected: !0, reason: o })
                                  : m({ targetEvent: e, args: t, callback: n });
                              });
                            };
                            return (t.invoke = t), t;
                          },
                          disconnectIssueText: o,
                          _fullSocketProps: p,
                        }
                      );
                    };
                    function le(e, t) {
                      (null == t || t > e.length) && (t = e.length);
                      for (var n = 0, r = new Array(t); n < t; n++) r[n] = e[n];
                      return r;
                    }
                    function se(e, t) {
                      var n = Object.keys(e);
                      if (Object.getOwnPropertySymbols) {
                        var r = Object.getOwnPropertySymbols(e);
                        t &&
                          (r = r.filter(function (t) {
                            return Object.getOwnPropertyDescriptor(
                              e,
                              t
                            ).enumerable;
                          })),
                          n.push.apply(n, r);
                      }
                      return n;
                    }
                    function ue(e) {
                      for (var t = 1; t < arguments.length; t++) {
                        var n = null != arguments[t] ? arguments[t] : {};
                        t % 2
                          ? se(Object(n), !0).forEach(function (t) {
                              ce(e, t, n[t]);
                            })
                          : Object.getOwnPropertyDescriptors
                          ? Object.defineProperties(
                              e,
                              Object.getOwnPropertyDescriptors(n)
                            )
                          : se(Object(n)).forEach(function (t) {
                              Object.defineProperty(
                                e,
                                t,
                                Object.getOwnPropertyDescriptor(n, t)
                              );
                            });
                      }
                      return e;
                    }
                    function ce(e, t, n) {
                      return (
                        t in e
                          ? Object.defineProperty(e, t, {
                              value: n,
                              enumerable: !0,
                              configurable: !0,
                              writable: !0,
                            })
                          : (e[t] = n),
                        e
                      );
                    }
                    var fe = function () {
                      var e,
                        n = getWorkerName(),
                        r = getAssignmentId(),
                        o = null === n || null === r,
                        i = {
                          providerWorkerId: n,
                          mephistoWorkerId: null,
                          agentId: null,
                          assignmentId: r,
                          taskConfig: null,
                          isPreview: o,
                          previewHtml: null,
                          blockedReason: null,
                          blockedExplanation: null,
                          initialTaskData: null,
                          isOnboarding: null,
                          loaded: !1,
                        },
                        a = t().useReducer(function (e, t) {
                          return ue(ue({}, e), t);
                        }, i),
                        l =
                          (function (e) {
                            if (Array.isArray(e)) return e;
                          })((e = a)) ||
                          (function (e, t) {
                            var n =
                              null == e
                                ? null
                                : ("undefined" != typeof Symbol &&
                                    e[Symbol.iterator]) ||
                                  e["@@iterator"];
                            if (null != n) {
                              var r,
                                o,
                                i = [],
                                a = !0,
                                l = !1;
                              try {
                                for (
                                  n = n.call(e);
                                  !(a = (r = n.next()).done) &&
                                  (i.push(r.value), 2 !== i.length);
                                  a = !0
                                );
                              } catch (e) {
                                (l = !0), (o = e);
                              } finally {
                                try {
                                  a || null == n.return || n.return();
                                } finally {
                                  if (l) throw o;
                                }
                              }
                              return i;
                            }
                          })(e) ||
                          (function (e, t) {
                            if (e) {
                              if ("string" == typeof e) return le(e, 2);
                              var n = Object.prototype.toString
                                .call(e)
                                .slice(8, -1);
                              return (
                                "Object" === n &&
                                  e.constructor &&
                                  (n = e.constructor.name),
                                "Map" === n || "Set" === n
                                  ? Array.from(e)
                                  : "Arguments" === n ||
                                    /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(
                                      n
                                    )
                                  ? le(e, 2)
                                  : void 0
                              );
                            }
                          })(e) ||
                          (function () {
                            throw new TypeError(
                              "Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."
                            );
                          })(),
                        s = l[0],
                        u = l[1],
                        c = t().useCallback(
                          function (e) {
                            s.isOnboarding
                              ? _(s.agentId, e).then(function (e) {
                                  p(e);
                                })
                              : S(s.agentId, e);
                          },
                          [s.agentId]
                        ),
                        f = t().useCallback(
                          function () {
                            for (
                              var e = {},
                                t = arguments.length,
                                n = new Array(t),
                                r = 0;
                              r < t;
                              r++
                            )
                              n[r] = arguments[r];
                            for (var o = 0, i = n; o < i.length; o++) {
                              var a = i[o];
                              if (a && a.hasOwnProperty("type")) {
                                var l = a.type;
                                e[l] = a;
                              }
                            }
                            return new Promise(function (t, n) {
                              t(T(s.agentId, e));
                            });
                          },
                          [s.agentId]
                        ),
                        d = t().useCallback(
                          function (e) {
                            O(s.agentId, e);
                          },
                          [s.agentId]
                        );
                      function p(e) {
                        var t = e.data.worker_id,
                          n = e.data.agent_id,
                          r = null !== n && n.startsWith("onboarding");
                        u({ agentId: n, isOnboarding: r }),
                          u(
                            null === n
                              ? {
                                  mephistoWorkerId: t,
                                  agentId: n,
                                  blockedReason: "null_agent_id",
                                  blockedExplanation: e.data.failure_reason,
                                }
                              : {
                                  mephistoWorkerId: t,
                                  mephistoAgentId: n,
                                  initialTaskData: e.data.init_task_data,
                                  loaded: !0,
                                }
                          );
                      }
                      return (
                        t().useEffect(function () {
                          x().then(function (e) {
                            return (
                              (t = e).block_mobile && v()
                                ? u({ blockedReason: "no_mobile" })
                                : s.isPreview ||
                                  E().then(function (e) {
                                    console.log(e), p(e);
                                  }),
                              void u({ taskConfig: t, loaded: o })
                            );
                            var t;
                          });
                        }, []),
                        ue(
                          ue({}, s),
                          {},
                          {
                            isLoading: !s.loaded,
                            blockedExplanation:
                              s.blockedExplanation ||
                              (s.blockedReason && P(s.blockedReason)),
                            handleSubmit: c,
                            handleMetadataSubmit: f,
                            handleFatalError: d,
                          }
                        )
                      );
                    };
                  })(),
                  o
                );
              })();
            }),
            "object" == l(t) && "object" == l(e)
              ? (e.exports = a(n(156)))
              : ((o = [n(156)]),
                void 0 ===
                  (i = "function" == typeof (r = a) ? r.apply(t, o) : r) ||
                  (e.exports = i));
        },
        191: (e, t, n) => {
          "use strict";
          n.d(t, { Z: () => l });
          var r = n(246),
            o = n.n(r),
            i = n(202),
            a = n.n(i)()(o());
          a.push([
            e.id,
            ".tooltip-container {\n  --tooltipBackground: #fff;\n  --tooltipBorder: #c0c0c0;\n  --tooltipColor: #000;\n\n  background-color: var(--tooltipBackground);\n  border-radius: 3px;\n  border: 1px solid var(--tooltipBorder);\n  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.18);\n  color: var(--tooltipColor);\n  display: flex;\n  flex-direction: column;\n  padding: 0.4rem;\n  transition: opacity 0.3s;\n  z-index: 9999;\n}\n\n.tooltip-container[data-popper-interactive='false'] {\n  pointer-events: none;\n}\n\n.tooltip-arrow {\n  height: 1rem;\n  position: absolute;\n  width: 1rem;\n  pointer-events: none;\n}\n\n.tooltip-arrow::before {\n  border-style: solid;\n  content: '';\n  display: block;\n  height: 0;\n  margin: auto;\n  width: 0;\n}\n\n.tooltip-arrow::after {\n  border-style: solid;\n  content: '';\n  display: block;\n  height: 0;\n  margin: auto;\n  position: absolute;\n  width: 0;\n}\n\n.tooltip-container[data-popper-placement*='bottom'] .tooltip-arrow {\n  left: 0;\n  margin-top: -0.4rem;\n  top: 0;\n}\n\n.tooltip-container[data-popper-placement*='bottom'] .tooltip-arrow::before {\n  border-color: transparent transparent var(--tooltipBorder) transparent;\n  border-width: 0 0.5rem 0.4rem 0.5rem;\n  position: absolute;\n  top: -1px;\n}\n\n.tooltip-container[data-popper-placement*='bottom'] .tooltip-arrow::after {\n  border-color: transparent transparent var(--tooltipBackground) transparent;\n  border-width: 0 0.5rem 0.4rem 0.5rem;\n}\n\n.tooltip-container[data-popper-placement*='top'] .tooltip-arrow {\n  bottom: 0;\n  left: 0;\n  margin-bottom: -1rem;\n}\n\n.tooltip-container[data-popper-placement*='top'] .tooltip-arrow::before {\n  border-color: var(--tooltipBorder) transparent transparent transparent;\n  border-width: 0.4rem 0.5rem 0 0.5rem;\n  position: absolute;\n  top: 1px;\n}\n\n.tooltip-container[data-popper-placement*='top'] .tooltip-arrow::after {\n  border-color: var(--tooltipBackground) transparent transparent transparent;\n  border-width: 0.4rem 0.5rem 0 0.5rem;\n}\n\n.tooltip-container[data-popper-placement*='right'] .tooltip-arrow {\n  left: 0;\n  margin-left: -0.7rem;\n}\n\n.tooltip-container[data-popper-placement*='right'] .tooltip-arrow::before {\n  border-color: transparent var(--tooltipBorder) transparent transparent;\n  border-width: 0.5rem 0.4rem 0.5rem 0;\n}\n\n.tooltip-container[data-popper-placement*='right'] .tooltip-arrow::after {\n  border-color: transparent var(--tooltipBackground) transparent transparent;\n  border-width: 0.5rem 0.4rem 0.5rem 0;\n  left: 6px;\n  top: 0;\n}\n\n.tooltip-container[data-popper-placement*='left'] .tooltip-arrow {\n  margin-right: -0.7rem;\n  right: 0;\n}\n\n.tooltip-container[data-popper-placement*='left'] .tooltip-arrow::before {\n  border-color: transparent transparent transparent var(--tooltipBorder);\n  border-width: 0.5rem 0 0.5rem 0.4em;\n}\n\n.tooltip-container[data-popper-placement*='left'] .tooltip-arrow::after {\n  border-color: transparent transparent transparent var(--tooltipBackground);\n  border-width: 0.5rem 0 0.5rem 0.4em;\n  left: 3px;\n  top: 0;\n}\n",
            "",
          ]);
          const l = a;
        },
        294: (e, t, n) => {
          "use strict";
          n.d(t, { Z: () => l });
          var r = n(246),
            o = n.n(r),
            i = n(202),
            a = n.n(i)()(o());
          a.push([
            e.id,
            '/* Headless Classes */\n.headless-mephisto-worker-addons-feedback__question {\n  display: block;\n  cursor: pointer;\n  overflow-wrap: break-word;\n}\n.headless-mephisto-worker-addons-feedback__header-items {\n  display: flex;\n  align-items: center;\n  flex-wrap: wrap;\n}\n\n.headless-mephisto-worker-addons-feedback__green-box,\n.headless-mephisto-worker-addons-feedback__red-box {\n  padding: 1rem;\n  width: min(18rem, 100%);\n  box-sizing: border-box;\n}\n\n.headless-mephisto-worker-addons-feedback__green-box {\n  background-color: #d1e7dd;\n  color: #315243;\n}\n\n.headless-mephisto-worker-addons-feedback__red-box {\n  background-color: #f8d7da;\n  color: #5c3c3f;\n}\n.headless-mephisto-worker-addons-feedback__items-horizontal {\n  display: flex;\n  align-items: center;\n}\n.headless-mephisto-worker-addons-feedback__subtitle {\n  font-style: italic;\n  font-size: 0.85em;\n  margin: 0;\n}\n\n/* Non-Headless Classes */\n.mephisto-worker-addons-feedback__button,\n.mephisto-worker-addons-feedback__button:hover,\n.mephisto-worker-addons-feedback__button:active,\n.mephisto-worker-addons-feedback__button:focus {\n  transition: background-color 200ms, box-shadow 200ms;\n}\n.mephisto-worker-addons-feedback__button {\n  padding: 0.65rem 0.75rem;\n  border-radius: 0.5rem;\n  cursor: pointer;\n  border: 0;\n  background-color: rgb(236, 236, 236);\n  font-size: 0.9em;\n  outline: none;\n  display: flex;\n  align-items: center;\n  min-height: 2.75rem;\n  width: fit-content;\n  margin: 0.5rem 0.25rem;\n}\n\n.mephisto-worker-addons-feedback__button:disabled {\n  cursor: not-allowed !important;\n  color: #969696;\n}\n\n.mephisto-worker-addons-feedback__button:hover {\n  background-color: rgb(230, 230, 230);\n  box-shadow: 0 0 0 0.1rem rgba(209, 209, 209, 0.5);\n}\n\n.mephisto-worker-addons-feedback__button:focus {\n  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.4);\n}\n\n.mephisto-worker-addons-feedback__question {\n  margin-bottom: 0.25rem;\n  display: block;\n  cursor: pointer;\n  overflow-wrap: break-word;\n  width: fit-content;\n}\n.mephisto-worker-addons-feedback__header1 {\n  font-weight: bold;\n  font-size: 1.4em;\n  margin: 0.75rem 0;\n}\n\n.mephisto-worker-addons-feedback__subtitle {\n  font-style: italic;\n  font-size: 0.85em;\n  color: rgb(97, 97, 97);\n  margin: 0 0 0 0.175rem;\n}\n\n.mephisto-worker-addons-feedback__header-items {\n  display: flex;\n  align-items: center;\n  margin-bottom: 0.75rem;\n  flex-wrap: wrap;\n}\n\n.mephisto-worker-addons-feedback__green-box,\n.mephisto-worker-addons-feedback__red-box {\n  padding: 1rem;\n  width: min(18rem, 100%);\n  border-radius: 0.5rem;\n  margin: 1rem 0 0.75rem;\n  box-sizing: border-box;\n}\n\n.mephisto-worker-addons-feedback__green-box {\n  background-color: #d1e7dd;\n  color: #315243;\n}\n\n.mephisto-worker-addons-feedback__red-box {\n  background-color: #f8d7da;\n  color: #5c3c3f;\n}\n\n/* Common Classes */\n.mephisto-worker-addons-feedback__container {\n  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen,\n    Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;\n  display: flex;\n  align-items: flex-start;\n  justify-content: flex-start;\n  background-color: rgb(245, 245, 245);\n  padding: 1.5rem;\n  border-radius: 1rem;\n  line-height: 1.5;\n  color: rgb(70, 70, 70);\n}\n\n.mephisto-worker-addons-feedback__questions-container {\n  margin-bottom: 0.5rem;\n}\n.mephisto-worker-addons-feedback__items-horizontal {\n  display: flex;\n  width: 100%;\n  flex-wrap: wrap;\n}\n\n.mephisto-worker-addons-feedback__items-vertical {\n  display: flex;\n  flex-direction: column;\n  width: 100%;\n}\n.mephisto-worker-addons-feedback__text-area:disabled {\n  cursor: not-allowed !important;\n}\n.mephisto-worker-addons-feedback__text-area {\n  min-width: min(8rem, 100%);\n  max-width: 100%;\n  min-height: 2.4rem;\n  height: 2.4rem;\n  max-height: 12rem;\n  background-color: rgb(240, 240, 240);\n  box-shadow: 0 0 0 0.15rem rgba(193, 193, 193, 0.5);\n  border: 0;\n  border-radius: 0.35rem;\n  padding: 0.5rem;\n  transition: background-color 200ms, box-shadow 200ms;\n  outline: none;\n  font-family: inherit;\n  font-size: 0.9em;\n  box-sizing: border-box;\n  transform: translateY(2.2px);\n  resize: vertical;\n  line-height: 1.5;\n  flex: 1;\n  margin: 0.5rem 0.25rem;\n}\n\n.mephisto-worker-addons-feedback__text-area-error {\n  box-shadow: 0 0 0 0.25rem rgba(241, 91, 91, 0.65) !important;\n  transition: background-color 200ms, box-shadow 200ms;\n}\n\n.mephisto-worker-addons-feedback__content-container {\n  margin: 0 0 1rem;\n  width: 100%;\n}\n.mephisto-worker-addons-feedback__text-area:hover {\n  background-color: rgb(245, 245, 245);\n  box-shadow: 0 0 0 0.2rem rgba(209, 209, 209, 0.5);\n  transition: background-color 200ms, box-shadow 200ms;\n}\n\n.mephisto-worker-addons-feedback__text-area:focus {\n  background-color: rgb(255, 255, 255);\n  transition: background-color 200ms, box-shadow 200ms;\n  box-shadow: 0 0 0 0.25rem rgba(0, 123, 255, 0.5);\n}\n\n.mephisto-worker-addons-feedback__vertical {\n  flex-direction: column;\n  align-items: flex-start;\n}\n\n.mephisto-worker-addons-feedback__loader {\n  width: 21px;\n  height: 21px;\n  border: 3px solid rgb(83, 83, 83);\n  border-bottom-color: transparent;\n  border-radius: 50%;\n  display: inline-block;\n  box-sizing: border-box;\n  animation: rotation 1s linear infinite;\n}\n@keyframes rotation {\n  0% {\n    transform: rotate(0deg);\n  }\n  100% {\n    transform: rotate(360deg);\n  }\n}\n',
            "",
          ]);
          const l = a;
        },
        202: (e) => {
          "use strict";
          e.exports = function (e) {
            var t = [];
            return (
              (t.toString = function () {
                return this.map(function (t) {
                  var n = "",
                    r = void 0 !== t[5];
                  return (
                    t[4] && (n += "@supports (".concat(t[4], ") {")),
                    t[2] && (n += "@media ".concat(t[2], " {")),
                    r &&
                      (n += "@layer".concat(
                        t[5].length > 0 ? " ".concat(t[5]) : "",
                        " {"
                      )),
                    (n += e(t)),
                    r && (n += "}"),
                    t[2] && (n += "}"),
                    t[4] && (n += "}"),
                    n
                  );
                }).join("");
              }),
              (t.i = function (e, n, r, o, i) {
                "string" == typeof e && (e = [[null, e, void 0]]);
                var a = {};
                if (r)
                  for (var l = 0; l < this.length; l++) {
                    var s = this[l][0];
                    null != s && (a[s] = !0);
                  }
                for (var u = 0; u < e.length; u++) {
                  var c = [].concat(e[u]);
                  (r && a[c[0]]) ||
                    (void 0 !== i &&
                      (void 0 === c[5] ||
                        (c[1] = "@layer"
                          .concat(c[5].length > 0 ? " ".concat(c[5]) : "", " {")
                          .concat(c[1], "}")),
                      (c[5] = i)),
                    n &&
                      (c[2]
                        ? ((c[1] = "@media "
                            .concat(c[2], " {")
                            .concat(c[1], "}")),
                          (c[2] = n))
                        : (c[2] = n)),
                    o &&
                      (c[4]
                        ? ((c[1] = "@supports ("
                            .concat(c[4], ") {")
                            .concat(c[1], "}")),
                          (c[4] = o))
                        : (c[4] = "".concat(o))),
                    t.push(c));
                }
              }),
              t
            );
          };
        },
        246: (e) => {
          "use strict";
          e.exports = function (e) {
            return e[1];
          };
        },
        145: (e, t, n) => {
          "use strict";
          var r = n(156),
            o = n(518),
            i = n(965);
          function a(e) {
            for (
              var t =
                  "https://reactjs.org/docs/error-decoder.html?invariant=" + e,
                n = 1;
              n < arguments.length;
              n++
            )
              t += "&args[]=" + encodeURIComponent(arguments[n]);
            return (
              "Minified React error #" +
              e +
              "; visit " +
              t +
              " for the full message or use the non-minified dev environment for full errors and additional helpful warnings."
            );
          }
          if (!r) throw Error(a(227));
          function l(e, t, n, r, o, i, a, l, s) {
            var u = Array.prototype.slice.call(arguments, 3);
            try {
              t.apply(n, u);
            } catch (e) {
              this.onError(e);
            }
          }
          var s = !1,
            u = null,
            c = !1,
            f = null,
            d = {
              onError: function (e) {
                (s = !0), (u = e);
              },
            };
          function p(e, t, n, r, o, i, a, c, f) {
            (s = !1), (u = null), l.apply(d, arguments);
          }
          var m = null,
            h = null,
            b = null;
          function g(e, t, n) {
            var r = e.type || "unknown-event";
            (e.currentTarget = b(n)),
              (function (e, t, n, r, o, i, l, d, m) {
                if ((p.apply(this, arguments), s)) {
                  if (!s) throw Error(a(198));
                  var h = u;
                  (s = !1), (u = null), c || ((c = !0), (f = h));
                }
              })(r, t, void 0, e),
              (e.currentTarget = null);
          }
          var v = null,
            y = {};
          function w() {
            if (v)
              for (var e in y) {
                var t = y[e],
                  n = v.indexOf(e);
                if (!(-1 < n)) throw Error(a(96, e));
                if (!k[n]) {
                  if (!t.extractEvents) throw Error(a(97, e));
                  for (var r in ((k[n] = t), (n = t.eventTypes))) {
                    var o = void 0,
                      i = n[r],
                      l = t,
                      s = r;
                    if (E.hasOwnProperty(s)) throw Error(a(99, s));
                    E[s] = i;
                    var u = i.phasedRegistrationNames;
                    if (u) {
                      for (o in u) u.hasOwnProperty(o) && x(u[o], l, s);
                      o = !0;
                    } else
                      i.registrationName
                        ? (x(i.registrationName, l, s), (o = !0))
                        : (o = !1);
                    if (!o) throw Error(a(98, r, e));
                  }
                }
              }
          }
          function x(e, t, n) {
            if (_[e]) throw Error(a(100, e));
            (_[e] = t), (S[e] = t.eventTypes[n].dependencies);
          }
          var k = [],
            E = {},
            _ = {},
            S = {};
          function T(e) {
            var t,
              n = !1;
            for (t in e)
              if (e.hasOwnProperty(t)) {
                var r = e[t];
                if (!y.hasOwnProperty(t) || y[t] !== r) {
                  if (y[t]) throw Error(a(102, t));
                  (y[t] = r), (n = !0);
                }
              }
            n && w();
          }
          var O = !(
              "undefined" == typeof window ||
              void 0 === window.document ||
              void 0 === window.document.createElement
            ),
            P = null,
            C = null,
            M = null;
          function N(e) {
            if ((e = h(e))) {
              if ("function" != typeof P) throw Error(a(280));
              var t = e.stateNode;
              t && ((t = m(t)), P(e.stateNode, e.type, t));
            }
          }
          function A(e) {
            C ? (M ? M.push(e) : (M = [e])) : (C = e);
          }
          function j() {
            if (C) {
              var e = C,
                t = M;
              if (((M = C = null), N(e), t))
                for (e = 0; e < t.length; e++) N(t[e]);
            }
          }
          function R(e, t) {
            return e(t);
          }
          function F(e, t, n, r, o) {
            return e(t, n, r, o);
          }
          function I() {}
          var L = R,
            z = !1,
            D = !1;
          function B() {
            (null === C && null === M) || (I(), j());
          }
          function U(e, t, n) {
            if (D) return e(t, n);
            D = !0;
            try {
              return L(e, t, n);
            } finally {
              (D = !1), B();
            }
          }
          var W = /^[:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$/,
            V = Object.prototype.hasOwnProperty,
            H = {},
            q = {};
          function Q(e, t, n, r, o, i) {
            (this.acceptsBooleans = 2 === t || 3 === t || 4 === t),
              (this.attributeName = r),
              (this.attributeNamespace = o),
              (this.mustUseProperty = n),
              (this.propertyName = e),
              (this.type = t),
              (this.sanitizeURL = i);
          }
          var K = {};
          "children dangerouslySetInnerHTML defaultValue defaultChecked innerHTML suppressContentEditableWarning suppressHydrationWarning style"
            .split(" ")
            .forEach(function (e) {
              K[e] = new Q(e, 0, !1, e, null, !1);
            }),
            [
              ["acceptCharset", "accept-charset"],
              ["className", "class"],
              ["htmlFor", "for"],
              ["httpEquiv", "http-equiv"],
            ].forEach(function (e) {
              var t = e[0];
              K[t] = new Q(t, 1, !1, e[1], null, !1);
            }),
            ["contentEditable", "draggable", "spellCheck", "value"].forEach(
              function (e) {
                K[e] = new Q(e, 2, !1, e.toLowerCase(), null, !1);
              }
            ),
            [
              "autoReverse",
              "externalResourcesRequired",
              "focusable",
              "preserveAlpha",
            ].forEach(function (e) {
              K[e] = new Q(e, 2, !1, e, null, !1);
            }),
            "allowFullScreen async autoFocus autoPlay controls default defer disabled disablePictureInPicture formNoValidate hidden loop noModule noValidate open playsInline readOnly required reversed scoped seamless itemScope"
              .split(" ")
              .forEach(function (e) {
                K[e] = new Q(e, 3, !1, e.toLowerCase(), null, !1);
              }),
            ["checked", "multiple", "muted", "selected"].forEach(function (e) {
              K[e] = new Q(e, 3, !0, e, null, !1);
            }),
            ["capture", "download"].forEach(function (e) {
              K[e] = new Q(e, 4, !1, e, null, !1);
            }),
            ["cols", "rows", "size", "span"].forEach(function (e) {
              K[e] = new Q(e, 6, !1, e, null, !1);
            }),
            ["rowSpan", "start"].forEach(function (e) {
              K[e] = new Q(e, 5, !1, e.toLowerCase(), null, !1);
            });
          var G = /[\-:]([a-z])/g;
          function $(e) {
            return e[1].toUpperCase();
          }
          "accent-height alignment-baseline arabic-form baseline-shift cap-height clip-path clip-rule color-interpolation color-interpolation-filters color-profile color-rendering dominant-baseline enable-background fill-opacity fill-rule flood-color flood-opacity font-family font-size font-size-adjust font-stretch font-style font-variant font-weight glyph-name glyph-orientation-horizontal glyph-orientation-vertical horiz-adv-x horiz-origin-x image-rendering letter-spacing lighting-color marker-end marker-mid marker-start overline-position overline-thickness paint-order panose-1 pointer-events rendering-intent shape-rendering stop-color stop-opacity strikethrough-position strikethrough-thickness stroke-dasharray stroke-dashoffset stroke-linecap stroke-linejoin stroke-miterlimit stroke-opacity stroke-width text-anchor text-decoration text-rendering underline-position underline-thickness unicode-bidi unicode-range units-per-em v-alphabetic v-hanging v-ideographic v-mathematical vector-effect vert-adv-y vert-origin-x vert-origin-y word-spacing writing-mode xmlns:xlink x-height"
            .split(" ")
            .forEach(function (e) {
              var t = e.replace(G, $);
              K[t] = new Q(t, 1, !1, e, null, !1);
            }),
            "xlink:actuate xlink:arcrole xlink:role xlink:show xlink:title xlink:type"
              .split(" ")
              .forEach(function (e) {
                var t = e.replace(G, $);
                K[t] = new Q(t, 1, !1, e, "http://www.w3.org/1999/xlink", !1);
              }),
            ["xml:base", "xml:lang", "xml:space"].forEach(function (e) {
              var t = e.replace(G, $);
              K[t] = new Q(
                t,
                1,
                !1,
                e,
                "http://www.w3.org/XML/1998/namespace",
                !1
              );
            }),
            ["tabIndex", "crossOrigin"].forEach(function (e) {
              K[e] = new Q(e, 1, !1, e.toLowerCase(), null, !1);
            }),
            (K.xlinkHref = new Q(
              "xlinkHref",
              1,
              !1,
              "xlink:href",
              "http://www.w3.org/1999/xlink",
              !0
            )),
            ["src", "href", "action", "formAction"].forEach(function (e) {
              K[e] = new Q(e, 1, !1, e.toLowerCase(), null, !0);
            });
          var Y = r.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED;
          function X(e, t, n, r) {
            var o = K.hasOwnProperty(t) ? K[t] : null;
            (null !== o
              ? 0 === o.type
              : !r &&
                2 < t.length &&
                ("o" === t[0] || "O" === t[0]) &&
                ("n" === t[1] || "N" === t[1])) ||
              ((function (e, t, n, r) {
                if (
                  null == t ||
                  (function (e, t, n, r) {
                    if (null !== n && 0 === n.type) return !1;
                    switch (typeof t) {
                      case "function":
                      case "symbol":
                        return !0;
                      case "boolean":
                        return (
                          !r &&
                          (null !== n
                            ? !n.acceptsBooleans
                            : "data-" !== (e = e.toLowerCase().slice(0, 5)) &&
                              "aria-" !== e)
                        );
                      default:
                        return !1;
                    }
                  })(e, t, n, r)
                )
                  return !0;
                if (r) return !1;
                if (null !== n)
                  switch (n.type) {
                    case 3:
                      return !t;
                    case 4:
                      return !1 === t;
                    case 5:
                      return isNaN(t);
                    case 6:
                      return isNaN(t) || 1 > t;
                  }
                return !1;
              })(t, n, o, r) && (n = null),
              r || null === o
                ? (function (e) {
                    return (
                      !!V.call(q, e) ||
                      (!V.call(H, e) &&
                        (W.test(e) ? (q[e] = !0) : ((H[e] = !0), !1)))
                    );
                  })(t) &&
                  (null === n
                    ? e.removeAttribute(t)
                    : e.setAttribute(t, "" + n))
                : o.mustUseProperty
                ? (e[o.propertyName] = null === n ? 3 !== o.type && "" : n)
                : ((t = o.attributeName),
                  (r = o.attributeNamespace),
                  null === n
                    ? e.removeAttribute(t)
                    : ((n =
                        3 === (o = o.type) || (4 === o && !0 === n)
                          ? ""
                          : "" + n),
                      r ? e.setAttributeNS(r, t, n) : e.setAttribute(t, n))));
          }
          Y.hasOwnProperty("ReactCurrentDispatcher") ||
            (Y.ReactCurrentDispatcher = { current: null }),
            Y.hasOwnProperty("ReactCurrentBatchConfig") ||
              (Y.ReactCurrentBatchConfig = { suspense: null });
          var Z = /^(.*)[\\\/]/,
            J = "function" == typeof Symbol && Symbol.for,
            ee = J ? Symbol.for("react.element") : 60103,
            te = J ? Symbol.for("react.portal") : 60106,
            ne = J ? Symbol.for("react.fragment") : 60107,
            re = J ? Symbol.for("react.strict_mode") : 60108,
            oe = J ? Symbol.for("react.profiler") : 60114,
            ie = J ? Symbol.for("react.provider") : 60109,
            ae = J ? Symbol.for("react.context") : 60110,
            le = J ? Symbol.for("react.concurrent_mode") : 60111,
            se = J ? Symbol.for("react.forward_ref") : 60112,
            ue = J ? Symbol.for("react.suspense") : 60113,
            ce = J ? Symbol.for("react.suspense_list") : 60120,
            fe = J ? Symbol.for("react.memo") : 60115,
            de = J ? Symbol.for("react.lazy") : 60116,
            pe = J ? Symbol.for("react.block") : 60121,
            me = "function" == typeof Symbol && Symbol.iterator;
          function he(e) {
            return null === e || "object" != typeof e
              ? null
              : "function" == typeof (e = (me && e[me]) || e["@@iterator"])
              ? e
              : null;
          }
          function be(e) {
            if (null == e) return null;
            if ("function" == typeof e) return e.displayName || e.name || null;
            if ("string" == typeof e) return e;
            switch (e) {
              case ne:
                return "Fragment";
              case te:
                return "Portal";
              case oe:
                return "Profiler";
              case re:
                return "StrictMode";
              case ue:
                return "Suspense";
              case ce:
                return "SuspenseList";
            }
            if ("object" == typeof e)
              switch (e.$$typeof) {
                case ae:
                  return "Context.Consumer";
                case ie:
                  return "Context.Provider";
                case se:
                  var t = e.render;
                  return (
                    (t = t.displayName || t.name || ""),
                    e.displayName ||
                      ("" !== t ? "ForwardRef(" + t + ")" : "ForwardRef")
                  );
                case fe:
                  return be(e.type);
                case pe:
                  return be(e.render);
                case de:
                  if ((e = 1 === e._status ? e._result : null)) return be(e);
              }
            return null;
          }
          function ge(e) {
            var t = "";
            do {
              e: switch (e.tag) {
                case 3:
                case 4:
                case 6:
                case 7:
                case 10:
                case 9:
                  var n = "";
                  break e;
                default:
                  var r = e._debugOwner,
                    o = e._debugSource,
                    i = be(e.type);
                  (n = null),
                    r && (n = be(r.type)),
                    (r = i),
                    (i = ""),
                    o
                      ? (i =
                          " (at " +
                          o.fileName.replace(Z, "") +
                          ":" +
                          o.lineNumber +
                          ")")
                      : n && (i = " (created by " + n + ")"),
                    (n = "\n    in " + (r || "Unknown") + i);
              }
              (t += n), (e = e.return);
            } while (e);
            return t;
          }
          function ve(e) {
            switch (typeof e) {
              case "boolean":
              case "number":
              case "object":
              case "string":
              case "undefined":
                return e;
              default:
                return "";
            }
          }
          function ye(e) {
            var t = e.type;
            return (
              (e = e.nodeName) &&
              "input" === e.toLowerCase() &&
              ("checkbox" === t || "radio" === t)
            );
          }
          function we(e) {
            e._valueTracker ||
              (e._valueTracker = (function (e) {
                var t = ye(e) ? "checked" : "value",
                  n = Object.getOwnPropertyDescriptor(
                    e.constructor.prototype,
                    t
                  ),
                  r = "" + e[t];
                if (
                  !e.hasOwnProperty(t) &&
                  void 0 !== n &&
                  "function" == typeof n.get &&
                  "function" == typeof n.set
                ) {
                  var o = n.get,
                    i = n.set;
                  return (
                    Object.defineProperty(e, t, {
                      configurable: !0,
                      get: function () {
                        return o.call(this);
                      },
                      set: function (e) {
                        (r = "" + e), i.call(this, e);
                      },
                    }),
                    Object.defineProperty(e, t, { enumerable: n.enumerable }),
                    {
                      getValue: function () {
                        return r;
                      },
                      setValue: function (e) {
                        r = "" + e;
                      },
                      stopTracking: function () {
                        (e._valueTracker = null), delete e[t];
                      },
                    }
                  );
                }
              })(e));
          }
          function xe(e) {
            if (!e) return !1;
            var t = e._valueTracker;
            if (!t) return !0;
            var n = t.getValue(),
              r = "";
            return (
              e && (r = ye(e) ? (e.checked ? "true" : "false") : e.value),
              (e = r) !== n && (t.setValue(e), !0)
            );
          }
          function ke(e, t) {
            var n = t.checked;
            return o({}, t, {
              defaultChecked: void 0,
              defaultValue: void 0,
              value: void 0,
              checked: null != n ? n : e._wrapperState.initialChecked,
            });
          }
          function Ee(e, t) {
            var n = null == t.defaultValue ? "" : t.defaultValue,
              r = null != t.checked ? t.checked : t.defaultChecked;
            (n = ve(null != t.value ? t.value : n)),
              (e._wrapperState = {
                initialChecked: r,
                initialValue: n,
                controlled:
                  "checkbox" === t.type || "radio" === t.type
                    ? null != t.checked
                    : null != t.value,
              });
          }
          function _e(e, t) {
            null != (t = t.checked) && X(e, "checked", t, !1);
          }
          function Se(e, t) {
            _e(e, t);
            var n = ve(t.value),
              r = t.type;
            if (null != n)
              "number" === r
                ? ((0 === n && "" === e.value) || e.value != n) &&
                  (e.value = "" + n)
                : e.value !== "" + n && (e.value = "" + n);
            else if ("submit" === r || "reset" === r)
              return void e.removeAttribute("value");
            t.hasOwnProperty("value")
              ? Oe(e, t.type, n)
              : t.hasOwnProperty("defaultValue") &&
                Oe(e, t.type, ve(t.defaultValue)),
              null == t.checked &&
                null != t.defaultChecked &&
                (e.defaultChecked = !!t.defaultChecked);
          }
          function Te(e, t, n) {
            if (t.hasOwnProperty("value") || t.hasOwnProperty("defaultValue")) {
              var r = t.type;
              if (
                !(
                  ("submit" !== r && "reset" !== r) ||
                  (void 0 !== t.value && null !== t.value)
                )
              )
                return;
              (t = "" + e._wrapperState.initialValue),
                n || t === e.value || (e.value = t),
                (e.defaultValue = t);
            }
            "" !== (n = e.name) && (e.name = ""),
              (e.defaultChecked = !!e._wrapperState.initialChecked),
              "" !== n && (e.name = n);
          }
          function Oe(e, t, n) {
            ("number" === t && e.ownerDocument.activeElement === e) ||
              (null == n
                ? (e.defaultValue = "" + e._wrapperState.initialValue)
                : e.defaultValue !== "" + n && (e.defaultValue = "" + n));
          }
          function Pe(e, t) {
            return (
              (e = o({ children: void 0 }, t)),
              (t = (function (e) {
                var t = "";
                return (
                  r.Children.forEach(e, function (e) {
                    null != e && (t += e);
                  }),
                  t
                );
              })(t.children)) && (e.children = t),
              e
            );
          }
          function Ce(e, t, n, r) {
            if (((e = e.options), t)) {
              t = {};
              for (var o = 0; o < n.length; o++) t["$" + n[o]] = !0;
              for (n = 0; n < e.length; n++)
                (o = t.hasOwnProperty("$" + e[n].value)),
                  e[n].selected !== o && (e[n].selected = o),
                  o && r && (e[n].defaultSelected = !0);
            } else {
              for (n = "" + ve(n), t = null, o = 0; o < e.length; o++) {
                if (e[o].value === n)
                  return (
                    (e[o].selected = !0),
                    void (r && (e[o].defaultSelected = !0))
                  );
                null !== t || e[o].disabled || (t = e[o]);
              }
              null !== t && (t.selected = !0);
            }
          }
          function Me(e, t) {
            if (null != t.dangerouslySetInnerHTML) throw Error(a(91));
            return o({}, t, {
              value: void 0,
              defaultValue: void 0,
              children: "" + e._wrapperState.initialValue,
            });
          }
          function Ne(e, t) {
            var n = t.value;
            if (null == n) {
              if (((n = t.children), (t = t.defaultValue), null != n)) {
                if (null != t) throw Error(a(92));
                if (Array.isArray(n)) {
                  if (!(1 >= n.length)) throw Error(a(93));
                  n = n[0];
                }
                t = n;
              }
              null == t && (t = ""), (n = t);
            }
            e._wrapperState = { initialValue: ve(n) };
          }
          function Ae(e, t) {
            var n = ve(t.value),
              r = ve(t.defaultValue);
            null != n &&
              ((n = "" + n) !== e.value && (e.value = n),
              null == t.defaultValue &&
                e.defaultValue !== n &&
                (e.defaultValue = n)),
              null != r && (e.defaultValue = "" + r);
          }
          function je(e) {
            var t = e.textContent;
            t === e._wrapperState.initialValue &&
              "" !== t &&
              null !== t &&
              (e.value = t);
          }
          function Re(e) {
            switch (e) {
              case "svg":
                return "http://www.w3.org/2000/svg";
              case "math":
                return "http://www.w3.org/1998/Math/MathML";
              default:
                return "http://www.w3.org/1999/xhtml";
            }
          }
          function Fe(e, t) {
            return null == e || "http://www.w3.org/1999/xhtml" === e
              ? Re(t)
              : "http://www.w3.org/2000/svg" === e && "foreignObject" === t
              ? "http://www.w3.org/1999/xhtml"
              : e;
          }
          var Ie,
            Le,
            ze =
              ((Le = function (e, t) {
                if (
                  "http://www.w3.org/2000/svg" !== e.namespaceURI ||
                  "innerHTML" in e
                )
                  e.innerHTML = t;
                else {
                  for (
                    (Ie = Ie || document.createElement("div")).innerHTML =
                      "<svg>" + t.valueOf().toString() + "</svg>",
                      t = Ie.firstChild;
                    e.firstChild;

                  )
                    e.removeChild(e.firstChild);
                  for (; t.firstChild; ) e.appendChild(t.firstChild);
                }
              }),
              "undefined" != typeof MSApp && MSApp.execUnsafeLocalFunction
                ? function (e, t, n, r) {
                    MSApp.execUnsafeLocalFunction(function () {
                      return Le(e, t);
                    });
                  }
                : Le);
          function De(e, t) {
            if (t) {
              var n = e.firstChild;
              if (n && n === e.lastChild && 3 === n.nodeType)
                return void (n.nodeValue = t);
            }
            e.textContent = t;
          }
          function Be(e, t) {
            var n = {};
            return (
              (n[e.toLowerCase()] = t.toLowerCase()),
              (n["Webkit" + e] = "webkit" + t),
              (n["Moz" + e] = "moz" + t),
              n
            );
          }
          var Ue = {
              animationend: Be("Animation", "AnimationEnd"),
              animationiteration: Be("Animation", "AnimationIteration"),
              animationstart: Be("Animation", "AnimationStart"),
              transitionend: Be("Transition", "TransitionEnd"),
            },
            We = {},
            Ve = {};
          function He(e) {
            if (We[e]) return We[e];
            if (!Ue[e]) return e;
            var t,
              n = Ue[e];
            for (t in n)
              if (n.hasOwnProperty(t) && t in Ve) return (We[e] = n[t]);
            return e;
          }
          O &&
            ((Ve = document.createElement("div").style),
            "AnimationEvent" in window ||
              (delete Ue.animationend.animation,
              delete Ue.animationiteration.animation,
              delete Ue.animationstart.animation),
            "TransitionEvent" in window || delete Ue.transitionend.transition);
          var qe = He("animationend"),
            Qe = He("animationiteration"),
            Ke = He("animationstart"),
            Ge = He("transitionend"),
            $e = "abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange seeked seeking stalled suspend timeupdate volumechange waiting".split(
              " "
            ),
            Ye = new ("function" == typeof WeakMap ? WeakMap : Map)();
          function Xe(e) {
            var t = Ye.get(e);
            return void 0 === t && ((t = new Map()), Ye.set(e, t)), t;
          }
          function Ze(e) {
            var t = e,
              n = e;
            if (e.alternate) for (; t.return; ) t = t.return;
            else {
              e = t;
              do {
                0 != (1026 & (t = e).effectTag) && (n = t.return),
                  (e = t.return);
              } while (e);
            }
            return 3 === t.tag ? n : null;
          }
          function Je(e) {
            if (13 === e.tag) {
              var t = e.memoizedState;
              if (
                (null === t &&
                  null !== (e = e.alternate) &&
                  (t = e.memoizedState),
                null !== t)
              )
                return t.dehydrated;
            }
            return null;
          }
          function et(e) {
            if (Ze(e) !== e) throw Error(a(188));
          }
          function tt(e, t) {
            if (null == t) throw Error(a(30));
            return null == e
              ? t
              : Array.isArray(e)
              ? Array.isArray(t)
                ? (e.push.apply(e, t), e)
                : (e.push(t), e)
              : Array.isArray(t)
              ? [e].concat(t)
              : [e, t];
          }
          function nt(e, t, n) {
            Array.isArray(e) ? e.forEach(t, n) : e && t.call(n, e);
          }
          var rt = null;
          function ot(e) {
            if (e) {
              var t = e._dispatchListeners,
                n = e._dispatchInstances;
              if (Array.isArray(t))
                for (var r = 0; r < t.length && !e.isPropagationStopped(); r++)
                  g(e, t[r], n[r]);
              else t && g(e, t, n);
              (e._dispatchListeners = null),
                (e._dispatchInstances = null),
                e.isPersistent() || e.constructor.release(e);
            }
          }
          function it(e) {
            if ((null !== e && (rt = tt(rt, e)), (e = rt), (rt = null), e)) {
              if ((nt(e, ot), rt)) throw Error(a(95));
              if (c) throw ((e = f), (c = !1), (f = null), e);
            }
          }
          function at(e) {
            return (
              (e = e.target || e.srcElement || window)
                .correspondingUseElement && (e = e.correspondingUseElement),
              3 === e.nodeType ? e.parentNode : e
            );
          }
          function lt(e) {
            if (!O) return !1;
            var t = (e = "on" + e) in document;
            return (
              t ||
                ((t = document.createElement("div")).setAttribute(e, "return;"),
                (t = "function" == typeof t[e])),
              t
            );
          }
          var st = [];
          function ut(e) {
            (e.topLevelType = null),
              (e.nativeEvent = null),
              (e.targetInst = null),
              (e.ancestors.length = 0),
              10 > st.length && st.push(e);
          }
          function ct(e, t, n, r) {
            if (st.length) {
              var o = st.pop();
              return (
                (o.topLevelType = e),
                (o.eventSystemFlags = r),
                (o.nativeEvent = t),
                (o.targetInst = n),
                o
              );
            }
            return {
              topLevelType: e,
              eventSystemFlags: r,
              nativeEvent: t,
              targetInst: n,
              ancestors: [],
            };
          }
          function ft(e) {
            var t = e.targetInst,
              n = t;
            do {
              if (!n) {
                e.ancestors.push(n);
                break;
              }
              var r = n;
              if (3 === r.tag) r = r.stateNode.containerInfo;
              else {
                for (; r.return; ) r = r.return;
                r = 3 !== r.tag ? null : r.stateNode.containerInfo;
              }
              if (!r) break;
              (5 !== (t = n.tag) && 6 !== t) || e.ancestors.push(n),
                (n = Pn(r));
            } while (n);
            for (n = 0; n < e.ancestors.length; n++) {
              t = e.ancestors[n];
              var o = at(e.nativeEvent);
              r = e.topLevelType;
              var i = e.nativeEvent,
                a = e.eventSystemFlags;
              0 === n && (a |= 64);
              for (var l = null, s = 0; s < k.length; s++) {
                var u = k[s];
                u && (u = u.extractEvents(r, t, i, o, a)) && (l = tt(l, u));
              }
              it(l);
            }
          }
          function dt(e, t, n) {
            if (!n.has(e)) {
              switch (e) {
                case "scroll":
                  Qt(t, "scroll", !0);
                  break;
                case "focus":
                case "blur":
                  Qt(t, "focus", !0),
                    Qt(t, "blur", !0),
                    n.set("blur", null),
                    n.set("focus", null);
                  break;
                case "cancel":
                case "close":
                  lt(e) && Qt(t, e, !0);
                  break;
                case "invalid":
                case "submit":
                case "reset":
                  break;
                default:
                  -1 === $e.indexOf(e) && qt(e, t);
              }
              n.set(e, null);
            }
          }
          var pt,
            mt,
            ht,
            bt = !1,
            gt = [],
            vt = null,
            yt = null,
            wt = null,
            xt = new Map(),
            kt = new Map(),
            Et = [],
            _t = "mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput close cancel copy cut paste click change contextmenu reset submit".split(
              " "
            ),
            St = "focus blur dragenter dragleave mouseover mouseout pointerover pointerout gotpointercapture lostpointercapture".split(
              " "
            );
          function Tt(e, t, n, r, o) {
            return {
              blockedOn: e,
              topLevelType: t,
              eventSystemFlags: 32 | n,
              nativeEvent: o,
              container: r,
            };
          }
          function Ot(e, t) {
            switch (e) {
              case "focus":
              case "blur":
                vt = null;
                break;
              case "dragenter":
              case "dragleave":
                yt = null;
                break;
              case "mouseover":
              case "mouseout":
                wt = null;
                break;
              case "pointerover":
              case "pointerout":
                xt.delete(t.pointerId);
                break;
              case "gotpointercapture":
              case "lostpointercapture":
                kt.delete(t.pointerId);
            }
          }
          function Pt(e, t, n, r, o, i) {
            return null === e || e.nativeEvent !== i
              ? ((e = Tt(t, n, r, o, i)),
                null !== t && null !== (t = Cn(t)) && mt(t),
                e)
              : ((e.eventSystemFlags |= r), e);
          }
          function Ct(e) {
            var t = Pn(e.target);
            if (null !== t) {
              var n = Ze(t);
              if (null !== n)
                if (13 === (t = n.tag)) {
                  if (null !== (t = Je(n)))
                    return (
                      (e.blockedOn = t),
                      void i.unstable_runWithPriority(e.priority, function () {
                        ht(n);
                      })
                    );
                } else if (3 === t && n.stateNode.hydrate)
                  return void (e.blockedOn =
                    3 === n.tag ? n.stateNode.containerInfo : null);
            }
            e.blockedOn = null;
          }
          function Mt(e) {
            if (null !== e.blockedOn) return !1;
            var t = Yt(
              e.topLevelType,
              e.eventSystemFlags,
              e.container,
              e.nativeEvent
            );
            if (null !== t) {
              var n = Cn(t);
              return null !== n && mt(n), (e.blockedOn = t), !1;
            }
            return !0;
          }
          function Nt(e, t, n) {
            Mt(e) && n.delete(t);
          }
          function At() {
            for (bt = !1; 0 < gt.length; ) {
              var e = gt[0];
              if (null !== e.blockedOn) {
                null !== (e = Cn(e.blockedOn)) && pt(e);
                break;
              }
              var t = Yt(
                e.topLevelType,
                e.eventSystemFlags,
                e.container,
                e.nativeEvent
              );
              null !== t ? (e.blockedOn = t) : gt.shift();
            }
            null !== vt && Mt(vt) && (vt = null),
              null !== yt && Mt(yt) && (yt = null),
              null !== wt && Mt(wt) && (wt = null),
              xt.forEach(Nt),
              kt.forEach(Nt);
          }
          function jt(e, t) {
            e.blockedOn === t &&
              ((e.blockedOn = null),
              bt ||
                ((bt = !0),
                i.unstable_scheduleCallback(i.unstable_NormalPriority, At)));
          }
          function Rt(e) {
            function t(t) {
              return jt(t, e);
            }
            if (0 < gt.length) {
              jt(gt[0], e);
              for (var n = 1; n < gt.length; n++) {
                var r = gt[n];
                r.blockedOn === e && (r.blockedOn = null);
              }
            }
            for (
              null !== vt && jt(vt, e),
                null !== yt && jt(yt, e),
                null !== wt && jt(wt, e),
                xt.forEach(t),
                kt.forEach(t),
                n = 0;
              n < Et.length;
              n++
            )
              (r = Et[n]).blockedOn === e && (r.blockedOn = null);
            for (; 0 < Et.length && null === (n = Et[0]).blockedOn; )
              Ct(n), null === n.blockedOn && Et.shift();
          }
          var Ft = {},
            It = new Map(),
            Lt = new Map(),
            zt = [
              "abort",
              "abort",
              qe,
              "animationEnd",
              Qe,
              "animationIteration",
              Ke,
              "animationStart",
              "canplay",
              "canPlay",
              "canplaythrough",
              "canPlayThrough",
              "durationchange",
              "durationChange",
              "emptied",
              "emptied",
              "encrypted",
              "encrypted",
              "ended",
              "ended",
              "error",
              "error",
              "gotpointercapture",
              "gotPointerCapture",
              "load",
              "load",
              "loadeddata",
              "loadedData",
              "loadedmetadata",
              "loadedMetadata",
              "loadstart",
              "loadStart",
              "lostpointercapture",
              "lostPointerCapture",
              "playing",
              "playing",
              "progress",
              "progress",
              "seeking",
              "seeking",
              "stalled",
              "stalled",
              "suspend",
              "suspend",
              "timeupdate",
              "timeUpdate",
              Ge,
              "transitionEnd",
              "waiting",
              "waiting",
            ];
          function Dt(e, t) {
            for (var n = 0; n < e.length; n += 2) {
              var r = e[n],
                o = e[n + 1],
                i = "on" + (o[0].toUpperCase() + o.slice(1));
              (i = {
                phasedRegistrationNames: {
                  bubbled: i,
                  captured: i + "Capture",
                },
                dependencies: [r],
                eventPriority: t,
              }),
                Lt.set(r, t),
                It.set(r, i),
                (Ft[o] = i);
            }
          }
          Dt(
            "blur blur cancel cancel click click close close contextmenu contextMenu copy copy cut cut auxclick auxClick dblclick doubleClick dragend dragEnd dragstart dragStart drop drop focus focus input input invalid invalid keydown keyDown keypress keyPress keyup keyUp mousedown mouseDown mouseup mouseUp paste paste pause pause play play pointercancel pointerCancel pointerdown pointerDown pointerup pointerUp ratechange rateChange reset reset seeked seeked submit submit touchcancel touchCancel touchend touchEnd touchstart touchStart volumechange volumeChange".split(
              " "
            ),
            0
          ),
            Dt(
              "drag drag dragenter dragEnter dragexit dragExit dragleave dragLeave dragover dragOver mousemove mouseMove mouseout mouseOut mouseover mouseOver pointermove pointerMove pointerout pointerOut pointerover pointerOver scroll scroll toggle toggle touchmove touchMove wheel wheel".split(
                " "
              ),
              1
            ),
            Dt(zt, 2);
          for (
            var Bt = "change selectionchange textInput compositionstart compositionend compositionupdate".split(
                " "
              ),
              Ut = 0;
            Ut < Bt.length;
            Ut++
          )
            Lt.set(Bt[Ut], 0);
          var Wt = i.unstable_UserBlockingPriority,
            Vt = i.unstable_runWithPriority,
            Ht = !0;
          function qt(e, t) {
            Qt(t, e, !1);
          }
          function Qt(e, t, n) {
            var r = Lt.get(t);
            switch (void 0 === r ? 2 : r) {
              case 0:
                r = Kt.bind(null, t, 1, e);
                break;
              case 1:
                r = Gt.bind(null, t, 1, e);
                break;
              default:
                r = $t.bind(null, t, 1, e);
            }
            n ? e.addEventListener(t, r, !0) : e.addEventListener(t, r, !1);
          }
          function Kt(e, t, n, r) {
            z || I();
            var o = $t,
              i = z;
            z = !0;
            try {
              F(o, e, t, n, r);
            } finally {
              (z = i) || B();
            }
          }
          function Gt(e, t, n, r) {
            Vt(Wt, $t.bind(null, e, t, n, r));
          }
          function $t(e, t, n, r) {
            if (Ht)
              if (0 < gt.length && -1 < _t.indexOf(e))
                (e = Tt(null, e, t, n, r)), gt.push(e);
              else {
                var o = Yt(e, t, n, r);
                if (null === o) Ot(e, r);
                else if (-1 < _t.indexOf(e))
                  (e = Tt(o, e, t, n, r)), gt.push(e);
                else if (
                  !(function (e, t, n, r, o) {
                    switch (t) {
                      case "focus":
                        return (vt = Pt(vt, e, t, n, r, o)), !0;
                      case "dragenter":
                        return (yt = Pt(yt, e, t, n, r, o)), !0;
                      case "mouseover":
                        return (wt = Pt(wt, e, t, n, r, o)), !0;
                      case "pointerover":
                        var i = o.pointerId;
                        return (
                          xt.set(i, Pt(xt.get(i) || null, e, t, n, r, o)), !0
                        );
                      case "gotpointercapture":
                        return (
                          (i = o.pointerId),
                          kt.set(i, Pt(kt.get(i) || null, e, t, n, r, o)),
                          !0
                        );
                    }
                    return !1;
                  })(o, e, t, n, r)
                ) {
                  Ot(e, r), (e = ct(e, r, null, t));
                  try {
                    U(ft, e);
                  } finally {
                    ut(e);
                  }
                }
              }
          }
          function Yt(e, t, n, r) {
            if (null !== (n = Pn((n = at(r))))) {
              var o = Ze(n);
              if (null === o) n = null;
              else {
                var i = o.tag;
                if (13 === i) {
                  if (null !== (n = Je(o))) return n;
                  n = null;
                } else if (3 === i) {
                  if (o.stateNode.hydrate)
                    return 3 === o.tag ? o.stateNode.containerInfo : null;
                  n = null;
                } else o !== n && (n = null);
              }
            }
            e = ct(e, r, n, t);
            try {
              U(ft, e);
            } finally {
              ut(e);
            }
            return null;
          }
          var Xt = {
              animationIterationCount: !0,
              borderImageOutset: !0,
              borderImageSlice: !0,
              borderImageWidth: !0,
              boxFlex: !0,
              boxFlexGroup: !0,
              boxOrdinalGroup: !0,
              columnCount: !0,
              columns: !0,
              flex: !0,
              flexGrow: !0,
              flexPositive: !0,
              flexShrink: !0,
              flexNegative: !0,
              flexOrder: !0,
              gridArea: !0,
              gridRow: !0,
              gridRowEnd: !0,
              gridRowSpan: !0,
              gridRowStart: !0,
              gridColumn: !0,
              gridColumnEnd: !0,
              gridColumnSpan: !0,
              gridColumnStart: !0,
              fontWeight: !0,
              lineClamp: !0,
              lineHeight: !0,
              opacity: !0,
              order: !0,
              orphans: !0,
              tabSize: !0,
              widows: !0,
              zIndex: !0,
              zoom: !0,
              fillOpacity: !0,
              floodOpacity: !0,
              stopOpacity: !0,
              strokeDasharray: !0,
              strokeDashoffset: !0,
              strokeMiterlimit: !0,
              strokeOpacity: !0,
              strokeWidth: !0,
            },
            Zt = ["Webkit", "ms", "Moz", "O"];
          function Jt(e, t, n) {
            return null == t || "boolean" == typeof t || "" === t
              ? ""
              : n ||
                "number" != typeof t ||
                0 === t ||
                (Xt.hasOwnProperty(e) && Xt[e])
              ? ("" + t).trim()
              : t + "px";
          }
          function en(e, t) {
            for (var n in ((e = e.style), t))
              if (t.hasOwnProperty(n)) {
                var r = 0 === n.indexOf("--"),
                  o = Jt(n, t[n], r);
                "float" === n && (n = "cssFloat"),
                  r ? e.setProperty(n, o) : (e[n] = o);
              }
          }
          Object.keys(Xt).forEach(function (e) {
            Zt.forEach(function (t) {
              (t = t + e.charAt(0).toUpperCase() + e.substring(1)),
                (Xt[t] = Xt[e]);
            });
          });
          var tn = o(
            { menuitem: !0 },
            {
              area: !0,
              base: !0,
              br: !0,
              col: !0,
              embed: !0,
              hr: !0,
              img: !0,
              input: !0,
              keygen: !0,
              link: !0,
              meta: !0,
              param: !0,
              source: !0,
              track: !0,
              wbr: !0,
            }
          );
          function nn(e, t) {
            if (t) {
              if (
                tn[e] &&
                (null != t.children || null != t.dangerouslySetInnerHTML)
              )
                throw Error(a(137, e, ""));
              if (null != t.dangerouslySetInnerHTML) {
                if (null != t.children) throw Error(a(60));
                if (
                  "object" != typeof t.dangerouslySetInnerHTML ||
                  !("__html" in t.dangerouslySetInnerHTML)
                )
                  throw Error(a(61));
              }
              if (null != t.style && "object" != typeof t.style)
                throw Error(a(62, ""));
            }
          }
          function rn(e, t) {
            if (-1 === e.indexOf("-")) return "string" == typeof t.is;
            switch (e) {
              case "annotation-xml":
              case "color-profile":
              case "font-face":
              case "font-face-src":
              case "font-face-uri":
              case "font-face-format":
              case "font-face-name":
              case "missing-glyph":
                return !1;
              default:
                return !0;
            }
          }
          var on = "http://www.w3.org/1999/xhtml";
          function an(e, t) {
            var n = Xe(
              (e = 9 === e.nodeType || 11 === e.nodeType ? e : e.ownerDocument)
            );
            t = S[t];
            for (var r = 0; r < t.length; r++) dt(t[r], e, n);
          }
          function ln() {}
          function sn(e) {
            if (
              void 0 ===
              (e = e || ("undefined" != typeof document ? document : void 0))
            )
              return null;
            try {
              return e.activeElement || e.body;
            } catch (t) {
              return e.body;
            }
          }
          function un(e) {
            for (; e && e.firstChild; ) e = e.firstChild;
            return e;
          }
          function cn(e, t) {
            var n,
              r = un(e);
            for (e = 0; r; ) {
              if (3 === r.nodeType) {
                if (((n = e + r.textContent.length), e <= t && n >= t))
                  return { node: r, offset: t - e };
                e = n;
              }
              e: {
                for (; r; ) {
                  if (r.nextSibling) {
                    r = r.nextSibling;
                    break e;
                  }
                  r = r.parentNode;
                }
                r = void 0;
              }
              r = un(r);
            }
          }
          function fn(e, t) {
            return (
              !(!e || !t) &&
              (e === t ||
                ((!e || 3 !== e.nodeType) &&
                  (t && 3 === t.nodeType
                    ? fn(e, t.parentNode)
                    : "contains" in e
                    ? e.contains(t)
                    : !!e.compareDocumentPosition &&
                      !!(16 & e.compareDocumentPosition(t)))))
            );
          }
          function dn() {
            for (var e = window, t = sn(); t instanceof e.HTMLIFrameElement; ) {
              try {
                var n = "string" == typeof t.contentWindow.location.href;
              } catch (e) {
                n = !1;
              }
              if (!n) break;
              t = sn((e = t.contentWindow).document);
            }
            return t;
          }
          function pn(e) {
            var t = e && e.nodeName && e.nodeName.toLowerCase();
            return (
              t &&
              (("input" === t &&
                ("text" === e.type ||
                  "search" === e.type ||
                  "tel" === e.type ||
                  "url" === e.type ||
                  "password" === e.type)) ||
                "textarea" === t ||
                "true" === e.contentEditable)
            );
          }
          var mn = "$?",
            hn = "$!",
            bn = null,
            gn = null;
          function vn(e, t) {
            switch (e) {
              case "button":
              case "input":
              case "select":
              case "textarea":
                return !!t.autoFocus;
            }
            return !1;
          }
          function yn(e, t) {
            return (
              "textarea" === e ||
              "option" === e ||
              "noscript" === e ||
              "string" == typeof t.children ||
              "number" == typeof t.children ||
              ("object" == typeof t.dangerouslySetInnerHTML &&
                null !== t.dangerouslySetInnerHTML &&
                null != t.dangerouslySetInnerHTML.__html)
            );
          }
          var wn = "function" == typeof setTimeout ? setTimeout : void 0,
            xn = "function" == typeof clearTimeout ? clearTimeout : void 0;
          function kn(e) {
            for (; null != e; e = e.nextSibling) {
              var t = e.nodeType;
              if (1 === t || 3 === t) break;
            }
            return e;
          }
          function En(e) {
            e = e.previousSibling;
            for (var t = 0; e; ) {
              if (8 === e.nodeType) {
                var n = e.data;
                if ("$" === n || n === hn || n === mn) {
                  if (0 === t) return e;
                  t--;
                } else "/$" === n && t++;
              }
              e = e.previousSibling;
            }
            return null;
          }
          var _n = Math.random().toString(36).slice(2),
            Sn = "__reactInternalInstance$" + _n,
            Tn = "__reactEventHandlers$" + _n,
            On = "__reactContainere$" + _n;
          function Pn(e) {
            var t = e[Sn];
            if (t) return t;
            for (var n = e.parentNode; n; ) {
              if ((t = n[On] || n[Sn])) {
                if (
                  ((n = t.alternate),
                  null !== t.child || (null !== n && null !== n.child))
                )
                  for (e = En(e); null !== e; ) {
                    if ((n = e[Sn])) return n;
                    e = En(e);
                  }
                return t;
              }
              n = (e = n).parentNode;
            }
            return null;
          }
          function Cn(e) {
            return !(e = e[Sn] || e[On]) ||
              (5 !== e.tag && 6 !== e.tag && 13 !== e.tag && 3 !== e.tag)
              ? null
              : e;
          }
          function Mn(e) {
            if (5 === e.tag || 6 === e.tag) return e.stateNode;
            throw Error(a(33));
          }
          function Nn(e) {
            return e[Tn] || null;
          }
          function An(e) {
            do {
              e = e.return;
            } while (e && 5 !== e.tag);
            return e || null;
          }
          function jn(e, t) {
            var n = e.stateNode;
            if (!n) return null;
            var r = m(n);
            if (!r) return null;
            n = r[t];
            e: switch (t) {
              case "onClick":
              case "onClickCapture":
              case "onDoubleClick":
              case "onDoubleClickCapture":
              case "onMouseDown":
              case "onMouseDownCapture":
              case "onMouseMove":
              case "onMouseMoveCapture":
              case "onMouseUp":
              case "onMouseUpCapture":
              case "onMouseEnter":
                (r = !r.disabled) ||
                  (r = !(
                    "button" === (e = e.type) ||
                    "input" === e ||
                    "select" === e ||
                    "textarea" === e
                  )),
                  (e = !r);
                break e;
              default:
                e = !1;
            }
            if (e) return null;
            if (n && "function" != typeof n) throw Error(a(231, t, typeof n));
            return n;
          }
          function Rn(e, t, n) {
            (t = jn(e, n.dispatchConfig.phasedRegistrationNames[t])) &&
              ((n._dispatchListeners = tt(n._dispatchListeners, t)),
              (n._dispatchInstances = tt(n._dispatchInstances, e)));
          }
          function Fn(e) {
            if (e && e.dispatchConfig.phasedRegistrationNames) {
              for (var t = e._targetInst, n = []; t; ) n.push(t), (t = An(t));
              for (t = n.length; 0 < t--; ) Rn(n[t], "captured", e);
              for (t = 0; t < n.length; t++) Rn(n[t], "bubbled", e);
            }
          }
          function In(e, t, n) {
            e &&
              n &&
              n.dispatchConfig.registrationName &&
              (t = jn(e, n.dispatchConfig.registrationName)) &&
              ((n._dispatchListeners = tt(n._dispatchListeners, t)),
              (n._dispatchInstances = tt(n._dispatchInstances, e)));
          }
          function Ln(e) {
            nt(e, Fn);
          }
          var zn = null,
            Dn = null,
            Bn = null;
          function Un() {
            if (Bn) return Bn;
            var e,
              t,
              n = Dn,
              r = n.length,
              o = "value" in zn ? zn.value : zn.textContent,
              i = o.length;
            for (e = 0; e < r && n[e] === o[e]; e++);
            var a = r - e;
            for (t = 1; t <= a && n[r - t] === o[i - t]; t++);
            return (Bn = o.slice(e, 1 < t ? 1 - t : void 0));
          }
          function Wn() {
            return !0;
          }
          function Vn() {
            return !1;
          }
          function Hn(e, t, n, r) {
            for (var o in ((this.dispatchConfig = e),
            (this._targetInst = t),
            (this.nativeEvent = n),
            (e = this.constructor.Interface)))
              e.hasOwnProperty(o) &&
                ((t = e[o])
                  ? (this[o] = t(n))
                  : "target" === o
                  ? (this.target = r)
                  : (this[o] = n[o]));
            return (
              (this.isDefaultPrevented = (
                null != n.defaultPrevented
                  ? n.defaultPrevented
                  : !1 === n.returnValue
              )
                ? Wn
                : Vn),
              (this.isPropagationStopped = Vn),
              this
            );
          }
          function qn(e, t, n, r) {
            if (this.eventPool.length) {
              var o = this.eventPool.pop();
              return this.call(o, e, t, n, r), o;
            }
            return new this(e, t, n, r);
          }
          function Qn(e) {
            if (!(e instanceof this)) throw Error(a(279));
            e.destructor(),
              10 > this.eventPool.length && this.eventPool.push(e);
          }
          function Kn(e) {
            (e.eventPool = []), (e.getPooled = qn), (e.release = Qn);
          }
          o(Hn.prototype, {
            preventDefault: function () {
              this.defaultPrevented = !0;
              var e = this.nativeEvent;
              e &&
                (e.preventDefault
                  ? e.preventDefault()
                  : "unknown" != typeof e.returnValue && (e.returnValue = !1),
                (this.isDefaultPrevented = Wn));
            },
            stopPropagation: function () {
              var e = this.nativeEvent;
              e &&
                (e.stopPropagation
                  ? e.stopPropagation()
                  : "unknown" != typeof e.cancelBubble && (e.cancelBubble = !0),
                (this.isPropagationStopped = Wn));
            },
            persist: function () {
              this.isPersistent = Wn;
            },
            isPersistent: Vn,
            destructor: function () {
              var e,
                t = this.constructor.Interface;
              for (e in t) this[e] = null;
              (this.nativeEvent = this._targetInst = this.dispatchConfig = null),
                (this.isPropagationStopped = this.isDefaultPrevented = Vn),
                (this._dispatchInstances = this._dispatchListeners = null);
            },
          }),
            (Hn.Interface = {
              type: null,
              target: null,
              currentTarget: function () {
                return null;
              },
              eventPhase: null,
              bubbles: null,
              cancelable: null,
              timeStamp: function (e) {
                return e.timeStamp || Date.now();
              },
              defaultPrevented: null,
              isTrusted: null,
            }),
            (Hn.extend = function (e) {
              function t() {}
              function n() {
                return r.apply(this, arguments);
              }
              var r = this;
              t.prototype = r.prototype;
              var i = new t();
              return (
                o(i, n.prototype),
                (n.prototype = i),
                (n.prototype.constructor = n),
                (n.Interface = o({}, r.Interface, e)),
                (n.extend = r.extend),
                Kn(n),
                n
              );
            }),
            Kn(Hn);
          var Gn = Hn.extend({ data: null }),
            $n = Hn.extend({ data: null }),
            Yn = [9, 13, 27, 32],
            Xn = O && "CompositionEvent" in window,
            Zn = null;
          O && "documentMode" in document && (Zn = document.documentMode);
          var Jn = O && "TextEvent" in window && !Zn,
            er = O && (!Xn || (Zn && 8 < Zn && 11 >= Zn)),
            tr = String.fromCharCode(32),
            nr = {
              beforeInput: {
                phasedRegistrationNames: {
                  bubbled: "onBeforeInput",
                  captured: "onBeforeInputCapture",
                },
                dependencies: [
                  "compositionend",
                  "keypress",
                  "textInput",
                  "paste",
                ],
              },
              compositionEnd: {
                phasedRegistrationNames: {
                  bubbled: "onCompositionEnd",
                  captured: "onCompositionEndCapture",
                },
                dependencies: "blur compositionend keydown keypress keyup mousedown".split(
                  " "
                ),
              },
              compositionStart: {
                phasedRegistrationNames: {
                  bubbled: "onCompositionStart",
                  captured: "onCompositionStartCapture",
                },
                dependencies: "blur compositionstart keydown keypress keyup mousedown".split(
                  " "
                ),
              },
              compositionUpdate: {
                phasedRegistrationNames: {
                  bubbled: "onCompositionUpdate",
                  captured: "onCompositionUpdateCapture",
                },
                dependencies: "blur compositionupdate keydown keypress keyup mousedown".split(
                  " "
                ),
              },
            },
            rr = !1;
          function or(e, t) {
            switch (e) {
              case "keyup":
                return -1 !== Yn.indexOf(t.keyCode);
              case "keydown":
                return 229 !== t.keyCode;
              case "keypress":
              case "mousedown":
              case "blur":
                return !0;
              default:
                return !1;
            }
          }
          function ir(e) {
            return "object" == typeof (e = e.detail) && "data" in e
              ? e.data
              : null;
          }
          var ar = !1,
            lr = {
              eventTypes: nr,
              extractEvents: function (e, t, n, r) {
                var o;
                if (Xn)
                  e: {
                    switch (e) {
                      case "compositionstart":
                        var i = nr.compositionStart;
                        break e;
                      case "compositionend":
                        i = nr.compositionEnd;
                        break e;
                      case "compositionupdate":
                        i = nr.compositionUpdate;
                        break e;
                    }
                    i = void 0;
                  }
                else
                  ar
                    ? or(e, n) && (i = nr.compositionEnd)
                    : "keydown" === e &&
                      229 === n.keyCode &&
                      (i = nr.compositionStart);
                return (
                  i
                    ? (er &&
                        "ko" !== n.locale &&
                        (ar || i !== nr.compositionStart
                          ? i === nr.compositionEnd && ar && (o = Un())
                          : ((Dn =
                              "value" in (zn = r) ? zn.value : zn.textContent),
                            (ar = !0))),
                      (i = Gn.getPooled(i, t, n, r)),
                      (o || null !== (o = ir(n))) && (i.data = o),
                      Ln(i),
                      (o = i))
                    : (o = null),
                  (e = Jn
                    ? (function (e, t) {
                        switch (e) {
                          case "compositionend":
                            return ir(t);
                          case "keypress":
                            return 32 !== t.which ? null : ((rr = !0), tr);
                          case "textInput":
                            return (e = t.data) === tr && rr ? null : e;
                          default:
                            return null;
                        }
                      })(e, n)
                    : (function (e, t) {
                        if (ar)
                          return "compositionend" === e || (!Xn && or(e, t))
                            ? ((e = Un()), (Bn = Dn = zn = null), (ar = !1), e)
                            : null;
                        switch (e) {
                          case "paste":
                          default:
                            return null;
                          case "keypress":
                            if (
                              !(t.ctrlKey || t.altKey || t.metaKey) ||
                              (t.ctrlKey && t.altKey)
                            ) {
                              if (t.char && 1 < t.char.length) return t.char;
                              if (t.which) return String.fromCharCode(t.which);
                            }
                            return null;
                          case "compositionend":
                            return er && "ko" !== t.locale ? null : t.data;
                        }
                      })(e, n))
                    ? (((t = $n.getPooled(nr.beforeInput, t, n, r)).data = e),
                      Ln(t))
                    : (t = null),
                  null === o ? t : null === t ? o : [o, t]
                );
              },
            },
            sr = {
              color: !0,
              date: !0,
              datetime: !0,
              "datetime-local": !0,
              email: !0,
              month: !0,
              number: !0,
              password: !0,
              range: !0,
              search: !0,
              tel: !0,
              text: !0,
              time: !0,
              url: !0,
              week: !0,
            };
          function ur(e) {
            var t = e && e.nodeName && e.nodeName.toLowerCase();
            return "input" === t ? !!sr[e.type] : "textarea" === t;
          }
          var cr = {
            change: {
              phasedRegistrationNames: {
                bubbled: "onChange",
                captured: "onChangeCapture",
              },
              dependencies: "blur change click focus input keydown keyup selectionchange".split(
                " "
              ),
            },
          };
          function fr(e, t, n) {
            return (
              ((e = Hn.getPooled(cr.change, e, t, n)).type = "change"),
              A(n),
              Ln(e),
              e
            );
          }
          var dr = null,
            pr = null;
          function mr(e) {
            it(e);
          }
          function hr(e) {
            if (xe(Mn(e))) return e;
          }
          function br(e, t) {
            if ("change" === e) return t;
          }
          var gr = !1;
          function vr() {
            dr && (dr.detachEvent("onpropertychange", yr), (pr = dr = null));
          }
          function yr(e) {
            if ("value" === e.propertyName && hr(pr))
              if (((e = fr(pr, e, at(e))), z)) it(e);
              else {
                z = !0;
                try {
                  R(mr, e);
                } finally {
                  (z = !1), B();
                }
              }
          }
          function wr(e, t, n) {
            "focus" === e
              ? (vr(), (pr = n), (dr = t).attachEvent("onpropertychange", yr))
              : "blur" === e && vr();
          }
          function xr(e) {
            if ("selectionchange" === e || "keyup" === e || "keydown" === e)
              return hr(pr);
          }
          function kr(e, t) {
            if ("click" === e) return hr(t);
          }
          function Er(e, t) {
            if ("input" === e || "change" === e) return hr(t);
          }
          O &&
            (gr =
              lt("input") &&
              (!document.documentMode || 9 < document.documentMode));
          var _r = {
              eventTypes: cr,
              _isInputEventSupported: gr,
              extractEvents: function (e, t, n, r) {
                var o = t ? Mn(t) : window,
                  i = o.nodeName && o.nodeName.toLowerCase();
                if ("select" === i || ("input" === i && "file" === o.type))
                  var a = br;
                else if (ur(o))
                  if (gr) a = Er;
                  else {
                    a = xr;
                    var l = wr;
                  }
                else
                  (i = o.nodeName) &&
                    "input" === i.toLowerCase() &&
                    ("checkbox" === o.type || "radio" === o.type) &&
                    (a = kr);
                if (a && (a = a(e, t))) return fr(a, n, r);
                l && l(e, o, t),
                  "blur" === e &&
                    (e = o._wrapperState) &&
                    e.controlled &&
                    "number" === o.type &&
                    Oe(o, "number", o.value);
              },
            },
            Sr = Hn.extend({ view: null, detail: null }),
            Tr = {
              Alt: "altKey",
              Control: "ctrlKey",
              Meta: "metaKey",
              Shift: "shiftKey",
            };
          function Or(e) {
            var t = this.nativeEvent;
            return t.getModifierState
              ? t.getModifierState(e)
              : !!(e = Tr[e]) && !!t[e];
          }
          function Pr() {
            return Or;
          }
          var Cr = 0,
            Mr = 0,
            Nr = !1,
            Ar = !1,
            jr = Sr.extend({
              screenX: null,
              screenY: null,
              clientX: null,
              clientY: null,
              pageX: null,
              pageY: null,
              ctrlKey: null,
              shiftKey: null,
              altKey: null,
              metaKey: null,
              getModifierState: Pr,
              button: null,
              buttons: null,
              relatedTarget: function (e) {
                return (
                  e.relatedTarget ||
                  (e.fromElement === e.srcElement ? e.toElement : e.fromElement)
                );
              },
              movementX: function (e) {
                if ("movementX" in e) return e.movementX;
                var t = Cr;
                return (
                  (Cr = e.screenX),
                  Nr
                    ? "mousemove" === e.type
                      ? e.screenX - t
                      : 0
                    : ((Nr = !0), 0)
                );
              },
              movementY: function (e) {
                if ("movementY" in e) return e.movementY;
                var t = Mr;
                return (
                  (Mr = e.screenY),
                  Ar
                    ? "mousemove" === e.type
                      ? e.screenY - t
                      : 0
                    : ((Ar = !0), 0)
                );
              },
            }),
            Rr = jr.extend({
              pointerId: null,
              width: null,
              height: null,
              pressure: null,
              tangentialPressure: null,
              tiltX: null,
              tiltY: null,
              twist: null,
              pointerType: null,
              isPrimary: null,
            }),
            Fr = {
              mouseEnter: {
                registrationName: "onMouseEnter",
                dependencies: ["mouseout", "mouseover"],
              },
              mouseLeave: {
                registrationName: "onMouseLeave",
                dependencies: ["mouseout", "mouseover"],
              },
              pointerEnter: {
                registrationName: "onPointerEnter",
                dependencies: ["pointerout", "pointerover"],
              },
              pointerLeave: {
                registrationName: "onPointerLeave",
                dependencies: ["pointerout", "pointerover"],
              },
            },
            Ir = {
              eventTypes: Fr,
              extractEvents: function (e, t, n, r, o) {
                var i = "mouseover" === e || "pointerover" === e,
                  a = "mouseout" === e || "pointerout" === e;
                if (
                  (i && 0 == (32 & o) && (n.relatedTarget || n.fromElement)) ||
                  (!a && !i)
                )
                  return null;
                if (
                  ((i =
                    r.window === r
                      ? r
                      : (i = r.ownerDocument)
                      ? i.defaultView || i.parentWindow
                      : window),
                  a
                    ? ((a = t),
                      null !==
                        (t = (t = n.relatedTarget || n.toElement)
                          ? Pn(t)
                          : null) &&
                        (t !== Ze(t) || (5 !== t.tag && 6 !== t.tag)) &&
                        (t = null))
                    : (a = null),
                  a === t)
                )
                  return null;
                if ("mouseout" === e || "mouseover" === e)
                  var l = jr,
                    s = Fr.mouseLeave,
                    u = Fr.mouseEnter,
                    c = "mouse";
                else
                  ("pointerout" !== e && "pointerover" !== e) ||
                    ((l = Rr),
                    (s = Fr.pointerLeave),
                    (u = Fr.pointerEnter),
                    (c = "pointer"));
                if (
                  ((e = null == a ? i : Mn(a)),
                  (i = null == t ? i : Mn(t)),
                  ((s = l.getPooled(s, a, n, r)).type = c + "leave"),
                  (s.target = e),
                  (s.relatedTarget = i),
                  ((n = l.getPooled(u, t, n, r)).type = c + "enter"),
                  (n.target = i),
                  (n.relatedTarget = e),
                  (c = t),
                  (r = a) && c)
                )
                  e: {
                    for (u = c, a = 0, e = l = r; e; e = An(e)) a++;
                    for (e = 0, t = u; t; t = An(t)) e++;
                    for (; 0 < a - e; ) (l = An(l)), a--;
                    for (; 0 < e - a; ) (u = An(u)), e--;
                    for (; a--; ) {
                      if (l === u || l === u.alternate) break e;
                      (l = An(l)), (u = An(u));
                    }
                    l = null;
                  }
                else l = null;
                for (
                  u = l, l = [];
                  r && r !== u && (null === (a = r.alternate) || a !== u);

                )
                  l.push(r), (r = An(r));
                for (
                  r = [];
                  c && c !== u && (null === (a = c.alternate) || a !== u);

                )
                  r.push(c), (c = An(c));
                for (c = 0; c < l.length; c++) In(l[c], "bubbled", s);
                for (c = r.length; 0 < c--; ) In(r[c], "captured", n);
                return 0 == (64 & o) ? [s] : [s, n];
              },
            },
            Lr =
              "function" == typeof Object.is
                ? Object.is
                : function (e, t) {
                    return (
                      (e === t && (0 !== e || 1 / e == 1 / t)) ||
                      (e != e && t != t)
                    );
                  },
            zr = Object.prototype.hasOwnProperty;
          function Dr(e, t) {
            if (Lr(e, t)) return !0;
            if (
              "object" != typeof e ||
              null === e ||
              "object" != typeof t ||
              null === t
            )
              return !1;
            var n = Object.keys(e),
              r = Object.keys(t);
            if (n.length !== r.length) return !1;
            for (r = 0; r < n.length; r++)
              if (!zr.call(t, n[r]) || !Lr(e[n[r]], t[n[r]])) return !1;
            return !0;
          }
          var Br =
              O && "documentMode" in document && 11 >= document.documentMode,
            Ur = {
              select: {
                phasedRegistrationNames: {
                  bubbled: "onSelect",
                  captured: "onSelectCapture",
                },
                dependencies: "blur contextmenu dragend focus keydown keyup mousedown mouseup selectionchange".split(
                  " "
                ),
              },
            },
            Wr = null,
            Vr = null,
            Hr = null,
            qr = !1;
          function Qr(e, t) {
            var n =
              t.window === t
                ? t.document
                : 9 === t.nodeType
                ? t
                : t.ownerDocument;
            return qr || null == Wr || Wr !== sn(n)
              ? null
              : ((n =
                  "selectionStart" in (n = Wr) && pn(n)
                    ? { start: n.selectionStart, end: n.selectionEnd }
                    : {
                        anchorNode: (n = (
                          (n.ownerDocument && n.ownerDocument.defaultView) ||
                          window
                        ).getSelection()).anchorNode,
                        anchorOffset: n.anchorOffset,
                        focusNode: n.focusNode,
                        focusOffset: n.focusOffset,
                      }),
                Hr && Dr(Hr, n)
                  ? null
                  : ((Hr = n),
                    ((e = Hn.getPooled(Ur.select, Vr, e, t)).type = "select"),
                    (e.target = Wr),
                    Ln(e),
                    e));
          }
          var Kr = {
              eventTypes: Ur,
              extractEvents: function (e, t, n, r, o, i) {
                if (
                  !(i = !(o =
                    i ||
                    (r.window === r
                      ? r.document
                      : 9 === r.nodeType
                      ? r
                      : r.ownerDocument)))
                ) {
                  e: {
                    (o = Xe(o)), (i = S.onSelect);
                    for (var a = 0; a < i.length; a++)
                      if (!o.has(i[a])) {
                        o = !1;
                        break e;
                      }
                    o = !0;
                  }
                  i = !o;
                }
                if (i) return null;
                switch (((o = t ? Mn(t) : window), e)) {
                  case "focus":
                    (ur(o) || "true" === o.contentEditable) &&
                      ((Wr = o), (Vr = t), (Hr = null));
                    break;
                  case "blur":
                    Hr = Vr = Wr = null;
                    break;
                  case "mousedown":
                    qr = !0;
                    break;
                  case "contextmenu":
                  case "mouseup":
                  case "dragend":
                    return (qr = !1), Qr(n, r);
                  case "selectionchange":
                    if (Br) break;
                  case "keydown":
                  case "keyup":
                    return Qr(n, r);
                }
                return null;
              },
            },
            Gr = Hn.extend({
              animationName: null,
              elapsedTime: null,
              pseudoElement: null,
            }),
            $r = Hn.extend({
              clipboardData: function (e) {
                return "clipboardData" in e
                  ? e.clipboardData
                  : window.clipboardData;
              },
            }),
            Yr = Sr.extend({ relatedTarget: null });
          function Xr(e) {
            var t = e.keyCode;
            return (
              "charCode" in e
                ? 0 === (e = e.charCode) && 13 === t && (e = 13)
                : (e = t),
              10 === e && (e = 13),
              32 <= e || 13 === e ? e : 0
            );
          }
          var Zr = {
              Esc: "Escape",
              Spacebar: " ",
              Left: "ArrowLeft",
              Up: "ArrowUp",
              Right: "ArrowRight",
              Down: "ArrowDown",
              Del: "Delete",
              Win: "OS",
              Menu: "ContextMenu",
              Apps: "ContextMenu",
              Scroll: "ScrollLock",
              MozPrintableKey: "Unidentified",
            },
            Jr = {
              8: "Backspace",
              9: "Tab",
              12: "Clear",
              13: "Enter",
              16: "Shift",
              17: "Control",
              18: "Alt",
              19: "Pause",
              20: "CapsLock",
              27: "Escape",
              32: " ",
              33: "PageUp",
              34: "PageDown",
              35: "End",
              36: "Home",
              37: "ArrowLeft",
              38: "ArrowUp",
              39: "ArrowRight",
              40: "ArrowDown",
              45: "Insert",
              46: "Delete",
              112: "F1",
              113: "F2",
              114: "F3",
              115: "F4",
              116: "F5",
              117: "F6",
              118: "F7",
              119: "F8",
              120: "F9",
              121: "F10",
              122: "F11",
              123: "F12",
              144: "NumLock",
              145: "ScrollLock",
              224: "Meta",
            },
            eo = Sr.extend({
              key: function (e) {
                if (e.key) {
                  var t = Zr[e.key] || e.key;
                  if ("Unidentified" !== t) return t;
                }
                return "keypress" === e.type
                  ? 13 === (e = Xr(e))
                    ? "Enter"
                    : String.fromCharCode(e)
                  : "keydown" === e.type || "keyup" === e.type
                  ? Jr[e.keyCode] || "Unidentified"
                  : "";
              },
              location: null,
              ctrlKey: null,
              shiftKey: null,
              altKey: null,
              metaKey: null,
              repeat: null,
              locale: null,
              getModifierState: Pr,
              charCode: function (e) {
                return "keypress" === e.type ? Xr(e) : 0;
              },
              keyCode: function (e) {
                return "keydown" === e.type || "keyup" === e.type
                  ? e.keyCode
                  : 0;
              },
              which: function (e) {
                return "keypress" === e.type
                  ? Xr(e)
                  : "keydown" === e.type || "keyup" === e.type
                  ? e.keyCode
                  : 0;
              },
            }),
            to = jr.extend({ dataTransfer: null }),
            no = Sr.extend({
              touches: null,
              targetTouches: null,
              changedTouches: null,
              altKey: null,
              metaKey: null,
              ctrlKey: null,
              shiftKey: null,
              getModifierState: Pr,
            }),
            ro = Hn.extend({
              propertyName: null,
              elapsedTime: null,
              pseudoElement: null,
            }),
            oo = jr.extend({
              deltaX: function (e) {
                return "deltaX" in e
                  ? e.deltaX
                  : "wheelDeltaX" in e
                  ? -e.wheelDeltaX
                  : 0;
              },
              deltaY: function (e) {
                return "deltaY" in e
                  ? e.deltaY
                  : "wheelDeltaY" in e
                  ? -e.wheelDeltaY
                  : "wheelDelta" in e
                  ? -e.wheelDelta
                  : 0;
              },
              deltaZ: null,
              deltaMode: null,
            }),
            io = {
              eventTypes: Ft,
              extractEvents: function (e, t, n, r) {
                var o = It.get(e);
                if (!o) return null;
                switch (e) {
                  case "keypress":
                    if (0 === Xr(n)) return null;
                  case "keydown":
                  case "keyup":
                    e = eo;
                    break;
                  case "blur":
                  case "focus":
                    e = Yr;
                    break;
                  case "click":
                    if (2 === n.button) return null;
                  case "auxclick":
                  case "dblclick":
                  case "mousedown":
                  case "mousemove":
                  case "mouseup":
                  case "mouseout":
                  case "mouseover":
                  case "contextmenu":
                    e = jr;
                    break;
                  case "drag":
                  case "dragend":
                  case "dragenter":
                  case "dragexit":
                  case "dragleave":
                  case "dragover":
                  case "dragstart":
                  case "drop":
                    e = to;
                    break;
                  case "touchcancel":
                  case "touchend":
                  case "touchmove":
                  case "touchstart":
                    e = no;
                    break;
                  case qe:
                  case Qe:
                  case Ke:
                    e = Gr;
                    break;
                  case Ge:
                    e = ro;
                    break;
                  case "scroll":
                    e = Sr;
                    break;
                  case "wheel":
                    e = oo;
                    break;
                  case "copy":
                  case "cut":
                  case "paste":
                    e = $r;
                    break;
                  case "gotpointercapture":
                  case "lostpointercapture":
                  case "pointercancel":
                  case "pointerdown":
                  case "pointermove":
                  case "pointerout":
                  case "pointerover":
                  case "pointerup":
                    e = Rr;
                    break;
                  default:
                    e = Hn;
                }
                return Ln((t = e.getPooled(o, t, n, r))), t;
              },
            };
          if (v) throw Error(a(101));
          (v = Array.prototype.slice.call(
            "ResponderEventPlugin SimpleEventPlugin EnterLeaveEventPlugin ChangeEventPlugin SelectEventPlugin BeforeInputEventPlugin".split(
              " "
            )
          )),
            w(),
            (m = Nn),
            (h = Cn),
            (b = Mn),
            T({
              SimpleEventPlugin: io,
              EnterLeaveEventPlugin: Ir,
              ChangeEventPlugin: _r,
              SelectEventPlugin: Kr,
              BeforeInputEventPlugin: lr,
            });
          var ao = [],
            lo = -1;
          function so(e) {
            0 > lo || ((e.current = ao[lo]), (ao[lo] = null), lo--);
          }
          function uo(e, t) {
            lo++, (ao[lo] = e.current), (e.current = t);
          }
          var co = {},
            fo = { current: co },
            po = { current: !1 },
            mo = co;
          function ho(e, t) {
            var n = e.type.contextTypes;
            if (!n) return co;
            var r = e.stateNode;
            if (r && r.__reactInternalMemoizedUnmaskedChildContext === t)
              return r.__reactInternalMemoizedMaskedChildContext;
            var o,
              i = {};
            for (o in n) i[o] = t[o];
            return (
              r &&
                (((e =
                  e.stateNode).__reactInternalMemoizedUnmaskedChildContext = t),
                (e.__reactInternalMemoizedMaskedChildContext = i)),
              i
            );
          }
          function bo(e) {
            return null != e.childContextTypes;
          }
          function go() {
            so(po), so(fo);
          }
          function vo(e, t, n) {
            if (fo.current !== co) throw Error(a(168));
            uo(fo, t), uo(po, n);
          }
          function yo(e, t, n) {
            var r = e.stateNode;
            if (
              ((e = t.childContextTypes),
              "function" != typeof r.getChildContext)
            )
              return n;
            for (var i in (r = r.getChildContext()))
              if (!(i in e)) throw Error(a(108, be(t) || "Unknown", i));
            return o({}, n, {}, r);
          }
          function wo(e) {
            return (
              (e =
                ((e = e.stateNode) &&
                  e.__reactInternalMemoizedMergedChildContext) ||
                co),
              (mo = fo.current),
              uo(fo, e),
              uo(po, po.current),
              !0
            );
          }
          function xo(e, t, n) {
            var r = e.stateNode;
            if (!r) throw Error(a(169));
            n
              ? ((e = yo(e, t, mo)),
                (r.__reactInternalMemoizedMergedChildContext = e),
                so(po),
                so(fo),
                uo(fo, e))
              : so(po),
              uo(po, n);
          }
          var ko = i.unstable_runWithPriority,
            Eo = i.unstable_scheduleCallback,
            _o = i.unstable_cancelCallback,
            So = i.unstable_requestPaint,
            To = i.unstable_now,
            Oo = i.unstable_getCurrentPriorityLevel,
            Po = i.unstable_ImmediatePriority,
            Co = i.unstable_UserBlockingPriority,
            Mo = i.unstable_NormalPriority,
            No = i.unstable_LowPriority,
            Ao = i.unstable_IdlePriority,
            jo = {},
            Ro = i.unstable_shouldYield,
            Fo = void 0 !== So ? So : function () {},
            Io = null,
            Lo = null,
            zo = !1,
            Do = To(),
            Bo =
              1e4 > Do
                ? To
                : function () {
                    return To() - Do;
                  };
          function Uo() {
            switch (Oo()) {
              case Po:
                return 99;
              case Co:
                return 98;
              case Mo:
                return 97;
              case No:
                return 96;
              case Ao:
                return 95;
              default:
                throw Error(a(332));
            }
          }
          function Wo(e) {
            switch (e) {
              case 99:
                return Po;
              case 98:
                return Co;
              case 97:
                return Mo;
              case 96:
                return No;
              case 95:
                return Ao;
              default:
                throw Error(a(332));
            }
          }
          function Vo(e, t) {
            return (e = Wo(e)), ko(e, t);
          }
          function Ho(e, t, n) {
            return (e = Wo(e)), Eo(e, t, n);
          }
          function qo(e) {
            return (
              null === Io ? ((Io = [e]), (Lo = Eo(Po, Ko))) : Io.push(e), jo
            );
          }
          function Qo() {
            if (null !== Lo) {
              var e = Lo;
              (Lo = null), _o(e);
            }
            Ko();
          }
          function Ko() {
            if (!zo && null !== Io) {
              zo = !0;
              var e = 0;
              try {
                var t = Io;
                Vo(99, function () {
                  for (; e < t.length; e++) {
                    var n = t[e];
                    do {
                      n = n(!0);
                    } while (null !== n);
                  }
                }),
                  (Io = null);
              } catch (t) {
                throw (null !== Io && (Io = Io.slice(e + 1)), Eo(Po, Qo), t);
              } finally {
                zo = !1;
              }
            }
          }
          function Go(e, t, n) {
            return (
              1073741821 -
              (1 + (((1073741821 - e + t / 10) / (n /= 10)) | 0)) * n
            );
          }
          function $o(e, t) {
            if (e && e.defaultProps)
              for (var n in ((t = o({}, t)), (e = e.defaultProps)))
                void 0 === t[n] && (t[n] = e[n]);
            return t;
          }
          var Yo = { current: null },
            Xo = null,
            Zo = null,
            Jo = null;
          function ei() {
            Jo = Zo = Xo = null;
          }
          function ti(e) {
            var t = Yo.current;
            so(Yo), (e.type._context._currentValue = t);
          }
          function ni(e, t) {
            for (; null !== e; ) {
              var n = e.alternate;
              if (e.childExpirationTime < t)
                (e.childExpirationTime = t),
                  null !== n &&
                    n.childExpirationTime < t &&
                    (n.childExpirationTime = t);
              else {
                if (!(null !== n && n.childExpirationTime < t)) break;
                n.childExpirationTime = t;
              }
              e = e.return;
            }
          }
          function ri(e, t) {
            (Xo = e),
              (Jo = Zo = null),
              null !== (e = e.dependencies) &&
                null !== e.firstContext &&
                (e.expirationTime >= t && (Ma = !0), (e.firstContext = null));
          }
          function oi(e, t) {
            if (Jo !== e && !1 !== t && 0 !== t)
              if (
                (("number" == typeof t && 1073741823 !== t) ||
                  ((Jo = e), (t = 1073741823)),
                (t = { context: e, observedBits: t, next: null }),
                null === Zo)
              ) {
                if (null === Xo) throw Error(a(308));
                (Zo = t),
                  (Xo.dependencies = {
                    expirationTime: 0,
                    firstContext: t,
                    responders: null,
                  });
              } else Zo = Zo.next = t;
            return e._currentValue;
          }
          var ii = !1;
          function ai(e) {
            e.updateQueue = {
              baseState: e.memoizedState,
              baseQueue: null,
              shared: { pending: null },
              effects: null,
            };
          }
          function li(e, t) {
            (e = e.updateQueue),
              t.updateQueue === e &&
                (t.updateQueue = {
                  baseState: e.baseState,
                  baseQueue: e.baseQueue,
                  shared: e.shared,
                  effects: e.effects,
                });
          }
          function si(e, t) {
            return ((e = {
              expirationTime: e,
              suspenseConfig: t,
              tag: 0,
              payload: null,
              callback: null,
              next: null,
            }).next = e);
          }
          function ui(e, t) {
            if (null !== (e = e.updateQueue)) {
              var n = (e = e.shared).pending;
              null === n ? (t.next = t) : ((t.next = n.next), (n.next = t)),
                (e.pending = t);
            }
          }
          function ci(e, t) {
            var n = e.alternate;
            null !== n && li(n, e),
              null === (n = (e = e.updateQueue).baseQueue)
                ? ((e.baseQueue = t.next = t), (t.next = t))
                : ((t.next = n.next), (n.next = t));
          }
          function fi(e, t, n, r) {
            var i = e.updateQueue;
            ii = !1;
            var a = i.baseQueue,
              l = i.shared.pending;
            if (null !== l) {
              if (null !== a) {
                var s = a.next;
                (a.next = l.next), (l.next = s);
              }
              (a = l),
                (i.shared.pending = null),
                null !== (s = e.alternate) &&
                  null !== (s = s.updateQueue) &&
                  (s.baseQueue = l);
            }
            if (null !== a) {
              s = a.next;
              var u = i.baseState,
                c = 0,
                f = null,
                d = null,
                p = null;
              if (null !== s)
                for (var m = s; ; ) {
                  if ((l = m.expirationTime) < r) {
                    var h = {
                      expirationTime: m.expirationTime,
                      suspenseConfig: m.suspenseConfig,
                      tag: m.tag,
                      payload: m.payload,
                      callback: m.callback,
                      next: null,
                    };
                    null === p ? ((d = p = h), (f = u)) : (p = p.next = h),
                      l > c && (c = l);
                  } else {
                    null !== p &&
                      (p = p.next = {
                        expirationTime: 1073741823,
                        suspenseConfig: m.suspenseConfig,
                        tag: m.tag,
                        payload: m.payload,
                        callback: m.callback,
                        next: null,
                      }),
                      is(l, m.suspenseConfig);
                    e: {
                      var b = e,
                        g = m;
                      switch (((l = t), (h = n), g.tag)) {
                        case 1:
                          if ("function" == typeof (b = g.payload)) {
                            u = b.call(h, u, l);
                            break e;
                          }
                          u = b;
                          break e;
                        case 3:
                          b.effectTag = (-4097 & b.effectTag) | 64;
                        case 0:
                          if (
                            null ==
                            (l =
                              "function" == typeof (b = g.payload)
                                ? b.call(h, u, l)
                                : b)
                          )
                            break e;
                          u = o({}, u, l);
                          break e;
                        case 2:
                          ii = !0;
                      }
                    }
                    null !== m.callback &&
                      ((e.effectTag |= 32),
                      null === (l = i.effects) ? (i.effects = [m]) : l.push(m));
                  }
                  if (null === (m = m.next) || m === s) {
                    if (null === (l = i.shared.pending)) break;
                    (m = a.next = l.next),
                      (l.next = s),
                      (i.baseQueue = a = l),
                      (i.shared.pending = null);
                  }
                }
              null === p ? (f = u) : (p.next = d),
                (i.baseState = f),
                (i.baseQueue = p),
                as(c),
                (e.expirationTime = c),
                (e.memoizedState = u);
            }
          }
          function di(e, t, n) {
            if (((e = t.effects), (t.effects = null), null !== e))
              for (t = 0; t < e.length; t++) {
                var r = e[t],
                  o = r.callback;
                if (null !== o) {
                  if (
                    ((r.callback = null),
                    (r = o),
                    (o = n),
                    "function" != typeof r)
                  )
                    throw Error(a(191, r));
                  r.call(o);
                }
              }
          }
          var pi = Y.ReactCurrentBatchConfig,
            mi = new r.Component().refs;
          function hi(e, t, n, r) {
            (n = null == (n = n(r, (t = e.memoizedState))) ? t : o({}, t, n)),
              (e.memoizedState = n),
              0 === e.expirationTime && (e.updateQueue.baseState = n);
          }
          var bi = {
            isMounted: function (e) {
              return !!(e = e._reactInternalFiber) && Ze(e) === e;
            },
            enqueueSetState: function (e, t, n) {
              e = e._reactInternalFiber;
              var r = Gl(),
                o = pi.suspense;
              ((o = si((r = $l(r, e, o)), o)).payload = t),
                null != n && (o.callback = n),
                ui(e, o),
                Yl(e, r);
            },
            enqueueReplaceState: function (e, t, n) {
              e = e._reactInternalFiber;
              var r = Gl(),
                o = pi.suspense;
              ((o = si((r = $l(r, e, o)), o)).tag = 1),
                (o.payload = t),
                null != n && (o.callback = n),
                ui(e, o),
                Yl(e, r);
            },
            enqueueForceUpdate: function (e, t) {
              e = e._reactInternalFiber;
              var n = Gl(),
                r = pi.suspense;
              ((r = si((n = $l(n, e, r)), r)).tag = 2),
                null != t && (r.callback = t),
                ui(e, r),
                Yl(e, n);
            },
          };
          function gi(e, t, n, r, o, i, a) {
            return "function" == typeof (e = e.stateNode).shouldComponentUpdate
              ? e.shouldComponentUpdate(r, i, a)
              : !(
                  t.prototype &&
                  t.prototype.isPureReactComponent &&
                  Dr(n, r) &&
                  Dr(o, i)
                );
          }
          function vi(e, t, n) {
            var r = !1,
              o = co,
              i = t.contextType;
            return (
              "object" == typeof i && null !== i
                ? (i = oi(i))
                : ((o = bo(t) ? mo : fo.current),
                  (i = (r = null != (r = t.contextTypes)) ? ho(e, o) : co)),
              (t = new t(n, i)),
              (e.memoizedState =
                null !== t.state && void 0 !== t.state ? t.state : null),
              (t.updater = bi),
              (e.stateNode = t),
              (t._reactInternalFiber = e),
              r &&
                (((e =
                  e.stateNode).__reactInternalMemoizedUnmaskedChildContext = o),
                (e.__reactInternalMemoizedMaskedChildContext = i)),
              t
            );
          }
          function yi(e, t, n, r) {
            (e = t.state),
              "function" == typeof t.componentWillReceiveProps &&
                t.componentWillReceiveProps(n, r),
              "function" == typeof t.UNSAFE_componentWillReceiveProps &&
                t.UNSAFE_componentWillReceiveProps(n, r),
              t.state !== e && bi.enqueueReplaceState(t, t.state, null);
          }
          function wi(e, t, n, r) {
            var o = e.stateNode;
            (o.props = n), (o.state = e.memoizedState), (o.refs = mi), ai(e);
            var i = t.contextType;
            "object" == typeof i && null !== i
              ? (o.context = oi(i))
              : ((i = bo(t) ? mo : fo.current), (o.context = ho(e, i))),
              fi(e, n, o, r),
              (o.state = e.memoizedState),
              "function" == typeof (i = t.getDerivedStateFromProps) &&
                (hi(e, t, i, n), (o.state = e.memoizedState)),
              "function" == typeof t.getDerivedStateFromProps ||
                "function" == typeof o.getSnapshotBeforeUpdate ||
                ("function" != typeof o.UNSAFE_componentWillMount &&
                  "function" != typeof o.componentWillMount) ||
                ((t = o.state),
                "function" == typeof o.componentWillMount &&
                  o.componentWillMount(),
                "function" == typeof o.UNSAFE_componentWillMount &&
                  o.UNSAFE_componentWillMount(),
                t !== o.state && bi.enqueueReplaceState(o, o.state, null),
                fi(e, n, o, r),
                (o.state = e.memoizedState)),
              "function" == typeof o.componentDidMount && (e.effectTag |= 4);
          }
          var xi = Array.isArray;
          function ki(e, t, n) {
            if (
              null !== (e = n.ref) &&
              "function" != typeof e &&
              "object" != typeof e
            ) {
              if (n._owner) {
                if ((n = n._owner)) {
                  if (1 !== n.tag) throw Error(a(309));
                  var r = n.stateNode;
                }
                if (!r) throw Error(a(147, e));
                var o = "" + e;
                return null !== t &&
                  null !== t.ref &&
                  "function" == typeof t.ref &&
                  t.ref._stringRef === o
                  ? t.ref
                  : ((t = function (e) {
                      var t = r.refs;
                      t === mi && (t = r.refs = {}),
                        null === e ? delete t[o] : (t[o] = e);
                    }),
                    (t._stringRef = o),
                    t);
              }
              if ("string" != typeof e) throw Error(a(284));
              if (!n._owner) throw Error(a(290, e));
            }
            return e;
          }
          function Ei(e, t) {
            if ("textarea" !== e.type)
              throw Error(
                a(
                  31,
                  "[object Object]" === Object.prototype.toString.call(t)
                    ? "object with keys {" + Object.keys(t).join(", ") + "}"
                    : t,
                  ""
                )
              );
          }
          function _i(e) {
            function t(t, n) {
              if (e) {
                var r = t.lastEffect;
                null !== r
                  ? ((r.nextEffect = n), (t.lastEffect = n))
                  : (t.firstEffect = t.lastEffect = n),
                  (n.nextEffect = null),
                  (n.effectTag = 8);
              }
            }
            function n(n, r) {
              if (!e) return null;
              for (; null !== r; ) t(n, r), (r = r.sibling);
              return null;
            }
            function r(e, t) {
              for (e = new Map(); null !== t; )
                null !== t.key ? e.set(t.key, t) : e.set(t.index, t),
                  (t = t.sibling);
              return e;
            }
            function o(e, t) {
              return ((e = Ts(e, t)).index = 0), (e.sibling = null), e;
            }
            function i(t, n, r) {
              return (
                (t.index = r),
                e
                  ? null !== (r = t.alternate)
                    ? (r = r.index) < n
                      ? ((t.effectTag = 2), n)
                      : r
                    : ((t.effectTag = 2), n)
                  : n
              );
            }
            function l(t) {
              return e && null === t.alternate && (t.effectTag = 2), t;
            }
            function s(e, t, n, r) {
              return null === t || 6 !== t.tag
                ? (((t = Cs(n, e.mode, r)).return = e), t)
                : (((t = o(t, n)).return = e), t);
            }
            function u(e, t, n, r) {
              return null !== t && t.elementType === n.type
                ? (((r = o(t, n.props)).ref = ki(e, t, n)), (r.return = e), r)
                : (((r = Os(n.type, n.key, n.props, null, e.mode, r)).ref = ki(
                    e,
                    t,
                    n
                  )),
                  (r.return = e),
                  r);
            }
            function c(e, t, n, r) {
              return null === t ||
                4 !== t.tag ||
                t.stateNode.containerInfo !== n.containerInfo ||
                t.stateNode.implementation !== n.implementation
                ? (((t = Ms(n, e.mode, r)).return = e), t)
                : (((t = o(t, n.children || [])).return = e), t);
            }
            function f(e, t, n, r, i) {
              return null === t || 7 !== t.tag
                ? (((t = Ps(n, e.mode, r, i)).return = e), t)
                : (((t = o(t, n)).return = e), t);
            }
            function d(e, t, n) {
              if ("string" == typeof t || "number" == typeof t)
                return ((t = Cs("" + t, e.mode, n)).return = e), t;
              if ("object" == typeof t && null !== t) {
                switch (t.$$typeof) {
                  case ee:
                    return (
                      ((n = Os(
                        t.type,
                        t.key,
                        t.props,
                        null,
                        e.mode,
                        n
                      )).ref = ki(e, null, t)),
                      (n.return = e),
                      n
                    );
                  case te:
                    return ((t = Ms(t, e.mode, n)).return = e), t;
                }
                if (xi(t) || he(t))
                  return ((t = Ps(t, e.mode, n, null)).return = e), t;
                Ei(e, t);
              }
              return null;
            }
            function p(e, t, n, r) {
              var o = null !== t ? t.key : null;
              if ("string" == typeof n || "number" == typeof n)
                return null !== o ? null : s(e, t, "" + n, r);
              if ("object" == typeof n && null !== n) {
                switch (n.$$typeof) {
                  case ee:
                    return n.key === o
                      ? n.type === ne
                        ? f(e, t, n.props.children, r, o)
                        : u(e, t, n, r)
                      : null;
                  case te:
                    return n.key === o ? c(e, t, n, r) : null;
                }
                if (xi(n) || he(n))
                  return null !== o ? null : f(e, t, n, r, null);
                Ei(e, n);
              }
              return null;
            }
            function m(e, t, n, r, o) {
              if ("string" == typeof r || "number" == typeof r)
                return s(t, (e = e.get(n) || null), "" + r, o);
              if ("object" == typeof r && null !== r) {
                switch (r.$$typeof) {
                  case ee:
                    return (
                      (e = e.get(null === r.key ? n : r.key) || null),
                      r.type === ne
                        ? f(t, e, r.props.children, o, r.key)
                        : u(t, e, r, o)
                    );
                  case te:
                    return c(
                      t,
                      (e = e.get(null === r.key ? n : r.key) || null),
                      r,
                      o
                    );
                }
                if (xi(r) || he(r))
                  return f(t, (e = e.get(n) || null), r, o, null);
                Ei(t, r);
              }
              return null;
            }
            function h(o, a, l, s) {
              for (
                var u = null, c = null, f = a, h = (a = 0), b = null;
                null !== f && h < l.length;
                h++
              ) {
                f.index > h ? ((b = f), (f = null)) : (b = f.sibling);
                var g = p(o, f, l[h], s);
                if (null === g) {
                  null === f && (f = b);
                  break;
                }
                e && f && null === g.alternate && t(o, f),
                  (a = i(g, a, h)),
                  null === c ? (u = g) : (c.sibling = g),
                  (c = g),
                  (f = b);
              }
              if (h === l.length) return n(o, f), u;
              if (null === f) {
                for (; h < l.length; h++)
                  null !== (f = d(o, l[h], s)) &&
                    ((a = i(f, a, h)),
                    null === c ? (u = f) : (c.sibling = f),
                    (c = f));
                return u;
              }
              for (f = r(o, f); h < l.length; h++)
                null !== (b = m(f, o, h, l[h], s)) &&
                  (e &&
                    null !== b.alternate &&
                    f.delete(null === b.key ? h : b.key),
                  (a = i(b, a, h)),
                  null === c ? (u = b) : (c.sibling = b),
                  (c = b));
              return (
                e &&
                  f.forEach(function (e) {
                    return t(o, e);
                  }),
                u
              );
            }
            function b(o, l, s, u) {
              var c = he(s);
              if ("function" != typeof c) throw Error(a(150));
              if (null == (s = c.call(s))) throw Error(a(151));
              for (
                var f = (c = null), h = l, b = (l = 0), g = null, v = s.next();
                null !== h && !v.done;
                b++, v = s.next()
              ) {
                h.index > b ? ((g = h), (h = null)) : (g = h.sibling);
                var y = p(o, h, v.value, u);
                if (null === y) {
                  null === h && (h = g);
                  break;
                }
                e && h && null === y.alternate && t(o, h),
                  (l = i(y, l, b)),
                  null === f ? (c = y) : (f.sibling = y),
                  (f = y),
                  (h = g);
              }
              if (v.done) return n(o, h), c;
              if (null === h) {
                for (; !v.done; b++, v = s.next())
                  null !== (v = d(o, v.value, u)) &&
                    ((l = i(v, l, b)),
                    null === f ? (c = v) : (f.sibling = v),
                    (f = v));
                return c;
              }
              for (h = r(o, h); !v.done; b++, v = s.next())
                null !== (v = m(h, o, b, v.value, u)) &&
                  (e &&
                    null !== v.alternate &&
                    h.delete(null === v.key ? b : v.key),
                  (l = i(v, l, b)),
                  null === f ? (c = v) : (f.sibling = v),
                  (f = v));
              return (
                e &&
                  h.forEach(function (e) {
                    return t(o, e);
                  }),
                c
              );
            }
            return function (e, r, i, s) {
              var u =
                "object" == typeof i &&
                null !== i &&
                i.type === ne &&
                null === i.key;
              u && (i = i.props.children);
              var c = "object" == typeof i && null !== i;
              if (c)
                switch (i.$$typeof) {
                  case ee:
                    e: {
                      for (c = i.key, u = r; null !== u; ) {
                        if (u.key === c) {
                          if (7 === u.tag) {
                            if (i.type === ne) {
                              n(e, u.sibling),
                                ((r = o(u, i.props.children)).return = e),
                                (e = r);
                              break e;
                            }
                          } else if (u.elementType === i.type) {
                            n(e, u.sibling),
                              ((r = o(u, i.props)).ref = ki(e, u, i)),
                              (r.return = e),
                              (e = r);
                            break e;
                          }
                          n(e, u);
                          break;
                        }
                        t(e, u), (u = u.sibling);
                      }
                      i.type === ne
                        ? (((r = Ps(
                            i.props.children,
                            e.mode,
                            s,
                            i.key
                          )).return = e),
                          (e = r))
                        : (((s = Os(
                            i.type,
                            i.key,
                            i.props,
                            null,
                            e.mode,
                            s
                          )).ref = ki(e, r, i)),
                          (s.return = e),
                          (e = s));
                    }
                    return l(e);
                  case te:
                    e: {
                      for (u = i.key; null !== r; ) {
                        if (r.key === u) {
                          if (
                            4 === r.tag &&
                            r.stateNode.containerInfo === i.containerInfo &&
                            r.stateNode.implementation === i.implementation
                          ) {
                            n(e, r.sibling),
                              ((r = o(r, i.children || [])).return = e),
                              (e = r);
                            break e;
                          }
                          n(e, r);
                          break;
                        }
                        t(e, r), (r = r.sibling);
                      }
                      ((r = Ms(i, e.mode, s)).return = e), (e = r);
                    }
                    return l(e);
                }
              if ("string" == typeof i || "number" == typeof i)
                return (
                  (i = "" + i),
                  null !== r && 6 === r.tag
                    ? (n(e, r.sibling), ((r = o(r, i)).return = e), (e = r))
                    : (n(e, r), ((r = Cs(i, e.mode, s)).return = e), (e = r)),
                  l(e)
                );
              if (xi(i)) return h(e, r, i, s);
              if (he(i)) return b(e, r, i, s);
              if ((c && Ei(e, i), void 0 === i && !u))
                switch (e.tag) {
                  case 1:
                  case 0:
                    throw (
                      ((e = e.type),
                      Error(a(152, e.displayName || e.name || "Component")))
                    );
                }
              return n(e, r);
            };
          }
          var Si = _i(!0),
            Ti = _i(!1),
            Oi = {},
            Pi = { current: Oi },
            Ci = { current: Oi },
            Mi = { current: Oi };
          function Ni(e) {
            if (e === Oi) throw Error(a(174));
            return e;
          }
          function Ai(e, t) {
            switch ((uo(Mi, t), uo(Ci, e), uo(Pi, Oi), (e = t.nodeType))) {
              case 9:
              case 11:
                t = (t = t.documentElement) ? t.namespaceURI : Fe(null, "");
                break;
              default:
                t = Fe(
                  (t = (e = 8 === e ? t.parentNode : t).namespaceURI || null),
                  (e = e.tagName)
                );
            }
            so(Pi), uo(Pi, t);
          }
          function ji() {
            so(Pi), so(Ci), so(Mi);
          }
          function Ri(e) {
            Ni(Mi.current);
            var t = Ni(Pi.current),
              n = Fe(t, e.type);
            t !== n && (uo(Ci, e), uo(Pi, n));
          }
          function Fi(e) {
            Ci.current === e && (so(Pi), so(Ci));
          }
          var Ii = { current: 0 };
          function Li(e) {
            for (var t = e; null !== t; ) {
              if (13 === t.tag) {
                var n = t.memoizedState;
                if (
                  null !== n &&
                  (null === (n = n.dehydrated) ||
                    n.data === mn ||
                    n.data === hn)
                )
                  return t;
              } else if (
                19 === t.tag &&
                void 0 !== t.memoizedProps.revealOrder
              ) {
                if (0 != (64 & t.effectTag)) return t;
              } else if (null !== t.child) {
                (t.child.return = t), (t = t.child);
                continue;
              }
              if (t === e) break;
              for (; null === t.sibling; ) {
                if (null === t.return || t.return === e) return null;
                t = t.return;
              }
              (t.sibling.return = t.return), (t = t.sibling);
            }
            return null;
          }
          function zi(e, t) {
            return { responder: e, props: t };
          }
          var Di = Y.ReactCurrentDispatcher,
            Bi = Y.ReactCurrentBatchConfig,
            Ui = 0,
            Wi = null,
            Vi = null,
            Hi = null,
            qi = !1;
          function Qi() {
            throw Error(a(321));
          }
          function Ki(e, t) {
            if (null === t) return !1;
            for (var n = 0; n < t.length && n < e.length; n++)
              if (!Lr(e[n], t[n])) return !1;
            return !0;
          }
          function Gi(e, t, n, r, o, i) {
            if (
              ((Ui = i),
              (Wi = t),
              (t.memoizedState = null),
              (t.updateQueue = null),
              (t.expirationTime = 0),
              (Di.current = null === e || null === e.memoizedState ? ga : va),
              (e = n(r, o)),
              t.expirationTime === Ui)
            ) {
              i = 0;
              do {
                if (((t.expirationTime = 0), !(25 > i))) throw Error(a(301));
                (i += 1),
                  (Hi = Vi = null),
                  (t.updateQueue = null),
                  (Di.current = ya),
                  (e = n(r, o));
              } while (t.expirationTime === Ui);
            }
            if (
              ((Di.current = ba),
              (t = null !== Vi && null !== Vi.next),
              (Ui = 0),
              (Hi = Vi = Wi = null),
              (qi = !1),
              t)
            )
              throw Error(a(300));
            return e;
          }
          function $i() {
            var e = {
              memoizedState: null,
              baseState: null,
              baseQueue: null,
              queue: null,
              next: null,
            };
            return (
              null === Hi ? (Wi.memoizedState = Hi = e) : (Hi = Hi.next = e), Hi
            );
          }
          function Yi() {
            if (null === Vi) {
              var e = Wi.alternate;
              e = null !== e ? e.memoizedState : null;
            } else e = Vi.next;
            var t = null === Hi ? Wi.memoizedState : Hi.next;
            if (null !== t) (Hi = t), (Vi = e);
            else {
              if (null === e) throw Error(a(310));
              (e = {
                memoizedState: (Vi = e).memoizedState,
                baseState: Vi.baseState,
                baseQueue: Vi.baseQueue,
                queue: Vi.queue,
                next: null,
              }),
                null === Hi ? (Wi.memoizedState = Hi = e) : (Hi = Hi.next = e);
            }
            return Hi;
          }
          function Xi(e, t) {
            return "function" == typeof t ? t(e) : t;
          }
          function Zi(e) {
            var t = Yi(),
              n = t.queue;
            if (null === n) throw Error(a(311));
            n.lastRenderedReducer = e;
            var r = Vi,
              o = r.baseQueue,
              i = n.pending;
            if (null !== i) {
              if (null !== o) {
                var l = o.next;
                (o.next = i.next), (i.next = l);
              }
              (r.baseQueue = o = i), (n.pending = null);
            }
            if (null !== o) {
              (o = o.next), (r = r.baseState);
              var s = (l = i = null),
                u = o;
              do {
                var c = u.expirationTime;
                if (c < Ui) {
                  var f = {
                    expirationTime: u.expirationTime,
                    suspenseConfig: u.suspenseConfig,
                    action: u.action,
                    eagerReducer: u.eagerReducer,
                    eagerState: u.eagerState,
                    next: null,
                  };
                  null === s ? ((l = s = f), (i = r)) : (s = s.next = f),
                    c > Wi.expirationTime && ((Wi.expirationTime = c), as(c));
                } else
                  null !== s &&
                    (s = s.next = {
                      expirationTime: 1073741823,
                      suspenseConfig: u.suspenseConfig,
                      action: u.action,
                      eagerReducer: u.eagerReducer,
                      eagerState: u.eagerState,
                      next: null,
                    }),
                    is(c, u.suspenseConfig),
                    (r = u.eagerReducer === e ? u.eagerState : e(r, u.action));
                u = u.next;
              } while (null !== u && u !== o);
              null === s ? (i = r) : (s.next = l),
                Lr(r, t.memoizedState) || (Ma = !0),
                (t.memoizedState = r),
                (t.baseState = i),
                (t.baseQueue = s),
                (n.lastRenderedState = r);
            }
            return [t.memoizedState, n.dispatch];
          }
          function Ji(e) {
            var t = Yi(),
              n = t.queue;
            if (null === n) throw Error(a(311));
            n.lastRenderedReducer = e;
            var r = n.dispatch,
              o = n.pending,
              i = t.memoizedState;
            if (null !== o) {
              n.pending = null;
              var l = (o = o.next);
              do {
                (i = e(i, l.action)), (l = l.next);
              } while (l !== o);
              Lr(i, t.memoizedState) || (Ma = !0),
                (t.memoizedState = i),
                null === t.baseQueue && (t.baseState = i),
                (n.lastRenderedState = i);
            }
            return [i, r];
          }
          function ea(e) {
            var t = $i();
            return (
              "function" == typeof e && (e = e()),
              (t.memoizedState = t.baseState = e),
              (e = (e = t.queue = {
                pending: null,
                dispatch: null,
                lastRenderedReducer: Xi,
                lastRenderedState: e,
              }).dispatch = ha.bind(null, Wi, e)),
              [t.memoizedState, e]
            );
          }
          function ta(e, t, n, r) {
            return (
              (e = { tag: e, create: t, destroy: n, deps: r, next: null }),
              null === (t = Wi.updateQueue)
                ? ((t = { lastEffect: null }),
                  (Wi.updateQueue = t),
                  (t.lastEffect = e.next = e))
                : null === (n = t.lastEffect)
                ? (t.lastEffect = e.next = e)
                : ((r = n.next),
                  (n.next = e),
                  (e.next = r),
                  (t.lastEffect = e)),
              e
            );
          }
          function na() {
            return Yi().memoizedState;
          }
          function ra(e, t, n, r) {
            var o = $i();
            (Wi.effectTag |= e),
              (o.memoizedState = ta(1 | t, n, void 0, void 0 === r ? null : r));
          }
          function oa(e, t, n, r) {
            var o = Yi();
            r = void 0 === r ? null : r;
            var i = void 0;
            if (null !== Vi) {
              var a = Vi.memoizedState;
              if (((i = a.destroy), null !== r && Ki(r, a.deps)))
                return void ta(t, n, i, r);
            }
            (Wi.effectTag |= e), (o.memoizedState = ta(1 | t, n, i, r));
          }
          function ia(e, t) {
            return ra(516, 4, e, t);
          }
          function aa(e, t) {
            return oa(516, 4, e, t);
          }
          function la(e, t) {
            return oa(4, 2, e, t);
          }
          function sa(e, t) {
            return "function" == typeof t
              ? ((e = e()),
                t(e),
                function () {
                  t(null);
                })
              : null != t
              ? ((e = e()),
                (t.current = e),
                function () {
                  t.current = null;
                })
              : void 0;
          }
          function ua(e, t, n) {
            return (
              (n = null != n ? n.concat([e]) : null),
              oa(4, 2, sa.bind(null, t, e), n)
            );
          }
          function ca() {}
          function fa(e, t) {
            return ($i().memoizedState = [e, void 0 === t ? null : t]), e;
          }
          function da(e, t) {
            var n = Yi();
            t = void 0 === t ? null : t;
            var r = n.memoizedState;
            return null !== r && null !== t && Ki(t, r[1])
              ? r[0]
              : ((n.memoizedState = [e, t]), e);
          }
          function pa(e, t) {
            var n = Yi();
            t = void 0 === t ? null : t;
            var r = n.memoizedState;
            return null !== r && null !== t && Ki(t, r[1])
              ? r[0]
              : ((e = e()), (n.memoizedState = [e, t]), e);
          }
          function ma(e, t, n) {
            var r = Uo();
            Vo(98 > r ? 98 : r, function () {
              e(!0);
            }),
              Vo(97 < r ? 97 : r, function () {
                var r = Bi.suspense;
                Bi.suspense = void 0 === t ? null : t;
                try {
                  e(!1), n();
                } finally {
                  Bi.suspense = r;
                }
              });
          }
          function ha(e, t, n) {
            var r = Gl(),
              o = pi.suspense;
            o = {
              expirationTime: (r = $l(r, e, o)),
              suspenseConfig: o,
              action: n,
              eagerReducer: null,
              eagerState: null,
              next: null,
            };
            var i = t.pending;
            if (
              (null === i ? (o.next = o) : ((o.next = i.next), (i.next = o)),
              (t.pending = o),
              (i = e.alternate),
              e === Wi || (null !== i && i === Wi))
            )
              (qi = !0), (o.expirationTime = Ui), (Wi.expirationTime = Ui);
            else {
              if (
                0 === e.expirationTime &&
                (null === i || 0 === i.expirationTime) &&
                null !== (i = t.lastRenderedReducer)
              )
                try {
                  var a = t.lastRenderedState,
                    l = i(a, n);
                  if (((o.eagerReducer = i), (o.eagerState = l), Lr(l, a)))
                    return;
                } catch (e) {}
              Yl(e, r);
            }
          }
          var ba = {
              readContext: oi,
              useCallback: Qi,
              useContext: Qi,
              useEffect: Qi,
              useImperativeHandle: Qi,
              useLayoutEffect: Qi,
              useMemo: Qi,
              useReducer: Qi,
              useRef: Qi,
              useState: Qi,
              useDebugValue: Qi,
              useResponder: Qi,
              useDeferredValue: Qi,
              useTransition: Qi,
            },
            ga = {
              readContext: oi,
              useCallback: fa,
              useContext: oi,
              useEffect: ia,
              useImperativeHandle: function (e, t, n) {
                return (
                  (n = null != n ? n.concat([e]) : null),
                  ra(4, 2, sa.bind(null, t, e), n)
                );
              },
              useLayoutEffect: function (e, t) {
                return ra(4, 2, e, t);
              },
              useMemo: function (e, t) {
                var n = $i();
                return (
                  (t = void 0 === t ? null : t),
                  (e = e()),
                  (n.memoizedState = [e, t]),
                  e
                );
              },
              useReducer: function (e, t, n) {
                var r = $i();
                return (
                  (t = void 0 !== n ? n(t) : t),
                  (r.memoizedState = r.baseState = t),
                  (e = (e = r.queue = {
                    pending: null,
                    dispatch: null,
                    lastRenderedReducer: e,
                    lastRenderedState: t,
                  }).dispatch = ha.bind(null, Wi, e)),
                  [r.memoizedState, e]
                );
              },
              useRef: function (e) {
                return (e = { current: e }), ($i().memoizedState = e);
              },
              useState: ea,
              useDebugValue: ca,
              useResponder: zi,
              useDeferredValue: function (e, t) {
                var n = ea(e),
                  r = n[0],
                  o = n[1];
                return (
                  ia(
                    function () {
                      var n = Bi.suspense;
                      Bi.suspense = void 0 === t ? null : t;
                      try {
                        o(e);
                      } finally {
                        Bi.suspense = n;
                      }
                    },
                    [e, t]
                  ),
                  r
                );
              },
              useTransition: function (e) {
                var t = ea(!1),
                  n = t[0];
                return (t = t[1]), [fa(ma.bind(null, t, e), [t, e]), n];
              },
            },
            va = {
              readContext: oi,
              useCallback: da,
              useContext: oi,
              useEffect: aa,
              useImperativeHandle: ua,
              useLayoutEffect: la,
              useMemo: pa,
              useReducer: Zi,
              useRef: na,
              useState: function () {
                return Zi(Xi);
              },
              useDebugValue: ca,
              useResponder: zi,
              useDeferredValue: function (e, t) {
                var n = Zi(Xi),
                  r = n[0],
                  o = n[1];
                return (
                  aa(
                    function () {
                      var n = Bi.suspense;
                      Bi.suspense = void 0 === t ? null : t;
                      try {
                        o(e);
                      } finally {
                        Bi.suspense = n;
                      }
                    },
                    [e, t]
                  ),
                  r
                );
              },
              useTransition: function (e) {
                var t = Zi(Xi),
                  n = t[0];
                return (t = t[1]), [da(ma.bind(null, t, e), [t, e]), n];
              },
            },
            ya = {
              readContext: oi,
              useCallback: da,
              useContext: oi,
              useEffect: aa,
              useImperativeHandle: ua,
              useLayoutEffect: la,
              useMemo: pa,
              useReducer: Ji,
              useRef: na,
              useState: function () {
                return Ji(Xi);
              },
              useDebugValue: ca,
              useResponder: zi,
              useDeferredValue: function (e, t) {
                var n = Ji(Xi),
                  r = n[0],
                  o = n[1];
                return (
                  aa(
                    function () {
                      var n = Bi.suspense;
                      Bi.suspense = void 0 === t ? null : t;
                      try {
                        o(e);
                      } finally {
                        Bi.suspense = n;
                      }
                    },
                    [e, t]
                  ),
                  r
                );
              },
              useTransition: function (e) {
                var t = Ji(Xi),
                  n = t[0];
                return (t = t[1]), [da(ma.bind(null, t, e), [t, e]), n];
              },
            },
            wa = null,
            xa = null,
            ka = !1;
          function Ea(e, t) {
            var n = _s(5, null, null, 0);
            (n.elementType = "DELETED"),
              (n.type = "DELETED"),
              (n.stateNode = t),
              (n.return = e),
              (n.effectTag = 8),
              null !== e.lastEffect
                ? ((e.lastEffect.nextEffect = n), (e.lastEffect = n))
                : (e.firstEffect = e.lastEffect = n);
          }
          function _a(e, t) {
            switch (e.tag) {
              case 5:
                var n = e.type;
                return (
                  null !==
                    (t =
                      1 !== t.nodeType ||
                      n.toLowerCase() !== t.nodeName.toLowerCase()
                        ? null
                        : t) && ((e.stateNode = t), !0)
                );
              case 6:
                return (
                  null !==
                    (t =
                      "" === e.pendingProps || 3 !== t.nodeType ? null : t) &&
                  ((e.stateNode = t), !0)
                );
              default:
                return !1;
            }
          }
          function Sa(e) {
            if (ka) {
              var t = xa;
              if (t) {
                var n = t;
                if (!_a(e, t)) {
                  if (!(t = kn(n.nextSibling)) || !_a(e, t))
                    return (
                      (e.effectTag = (-1025 & e.effectTag) | 2),
                      (ka = !1),
                      void (wa = e)
                    );
                  Ea(wa, n);
                }
                (wa = e), (xa = kn(t.firstChild));
              } else
                (e.effectTag = (-1025 & e.effectTag) | 2), (ka = !1), (wa = e);
            }
          }
          function Ta(e) {
            for (
              e = e.return;
              null !== e && 5 !== e.tag && 3 !== e.tag && 13 !== e.tag;

            )
              e = e.return;
            wa = e;
          }
          function Oa(e) {
            if (e !== wa) return !1;
            if (!ka) return Ta(e), (ka = !0), !1;
            var t = e.type;
            if (
              5 !== e.tag ||
              ("head" !== t && "body" !== t && !yn(t, e.memoizedProps))
            )
              for (t = xa; t; ) Ea(e, t), (t = kn(t.nextSibling));
            if ((Ta(e), 13 === e.tag)) {
              if (!(e = null !== (e = e.memoizedState) ? e.dehydrated : null))
                throw Error(a(317));
              e: {
                for (e = e.nextSibling, t = 0; e; ) {
                  if (8 === e.nodeType) {
                    var n = e.data;
                    if ("/$" === n) {
                      if (0 === t) {
                        xa = kn(e.nextSibling);
                        break e;
                      }
                      t--;
                    } else ("$" !== n && n !== hn && n !== mn) || t++;
                  }
                  e = e.nextSibling;
                }
                xa = null;
              }
            } else xa = wa ? kn(e.stateNode.nextSibling) : null;
            return !0;
          }
          function Pa() {
            (xa = wa = null), (ka = !1);
          }
          var Ca = Y.ReactCurrentOwner,
            Ma = !1;
          function Na(e, t, n, r) {
            t.child = null === e ? Ti(t, null, n, r) : Si(t, e.child, n, r);
          }
          function Aa(e, t, n, r, o) {
            n = n.render;
            var i = t.ref;
            return (
              ri(t, o),
              (r = Gi(e, t, n, r, i, o)),
              null === e || Ma
                ? ((t.effectTag |= 1), Na(e, t, r, o), t.child)
                : ((t.updateQueue = e.updateQueue),
                  (t.effectTag &= -517),
                  e.expirationTime <= o && (e.expirationTime = 0),
                  Ga(e, t, o))
            );
          }
          function ja(e, t, n, r, o, i) {
            if (null === e) {
              var a = n.type;
              return "function" != typeof a ||
                Ss(a) ||
                void 0 !== a.defaultProps ||
                null !== n.compare ||
                void 0 !== n.defaultProps
                ? (((e = Os(n.type, null, r, null, t.mode, i)).ref = t.ref),
                  (e.return = t),
                  (t.child = e))
                : ((t.tag = 15), (t.type = a), Ra(e, t, a, r, o, i));
            }
            return (
              (a = e.child),
              o < i &&
              ((o = a.memoizedProps),
              (n = null !== (n = n.compare) ? n : Dr)(o, r) && e.ref === t.ref)
                ? Ga(e, t, i)
                : ((t.effectTag |= 1),
                  ((e = Ts(a, r)).ref = t.ref),
                  (e.return = t),
                  (t.child = e))
            );
          }
          function Ra(e, t, n, r, o, i) {
            return null !== e &&
              Dr(e.memoizedProps, r) &&
              e.ref === t.ref &&
              ((Ma = !1), o < i)
              ? ((t.expirationTime = e.expirationTime), Ga(e, t, i))
              : Ia(e, t, n, r, i);
          }
          function Fa(e, t) {
            var n = t.ref;
            ((null === e && null !== n) || (null !== e && e.ref !== n)) &&
              (t.effectTag |= 128);
          }
          function Ia(e, t, n, r, o) {
            var i = bo(n) ? mo : fo.current;
            return (
              (i = ho(t, i)),
              ri(t, o),
              (n = Gi(e, t, n, r, i, o)),
              null === e || Ma
                ? ((t.effectTag |= 1), Na(e, t, n, o), t.child)
                : ((t.updateQueue = e.updateQueue),
                  (t.effectTag &= -517),
                  e.expirationTime <= o && (e.expirationTime = 0),
                  Ga(e, t, o))
            );
          }
          function La(e, t, n, r, o) {
            if (bo(n)) {
              var i = !0;
              wo(t);
            } else i = !1;
            if ((ri(t, o), null === t.stateNode))
              null !== e &&
                ((e.alternate = null),
                (t.alternate = null),
                (t.effectTag |= 2)),
                vi(t, n, r),
                wi(t, n, r, o),
                (r = !0);
            else if (null === e) {
              var a = t.stateNode,
                l = t.memoizedProps;
              a.props = l;
              var s = a.context,
                u = n.contextType;
              u =
                "object" == typeof u && null !== u
                  ? oi(u)
                  : ho(t, (u = bo(n) ? mo : fo.current));
              var c = n.getDerivedStateFromProps,
                f =
                  "function" == typeof c ||
                  "function" == typeof a.getSnapshotBeforeUpdate;
              f ||
                ("function" != typeof a.UNSAFE_componentWillReceiveProps &&
                  "function" != typeof a.componentWillReceiveProps) ||
                ((l !== r || s !== u) && yi(t, a, r, u)),
                (ii = !1);
              var d = t.memoizedState;
              (a.state = d),
                fi(t, r, a, o),
                (s = t.memoizedState),
                l !== r || d !== s || po.current || ii
                  ? ("function" == typeof c &&
                      (hi(t, n, c, r), (s = t.memoizedState)),
                    (l = ii || gi(t, n, l, r, d, s, u))
                      ? (f ||
                          ("function" != typeof a.UNSAFE_componentWillMount &&
                            "function" != typeof a.componentWillMount) ||
                          ("function" == typeof a.componentWillMount &&
                            a.componentWillMount(),
                          "function" == typeof a.UNSAFE_componentWillMount &&
                            a.UNSAFE_componentWillMount()),
                        "function" == typeof a.componentDidMount &&
                          (t.effectTag |= 4))
                      : ("function" == typeof a.componentDidMount &&
                          (t.effectTag |= 4),
                        (t.memoizedProps = r),
                        (t.memoizedState = s)),
                    (a.props = r),
                    (a.state = s),
                    (a.context = u),
                    (r = l))
                  : ("function" == typeof a.componentDidMount &&
                      (t.effectTag |= 4),
                    (r = !1));
            } else
              (a = t.stateNode),
                li(e, t),
                (l = t.memoizedProps),
                (a.props = t.type === t.elementType ? l : $o(t.type, l)),
                (s = a.context),
                (u =
                  "object" == typeof (u = n.contextType) && null !== u
                    ? oi(u)
                    : ho(t, (u = bo(n) ? mo : fo.current))),
                (f =
                  "function" == typeof (c = n.getDerivedStateFromProps) ||
                  "function" == typeof a.getSnapshotBeforeUpdate) ||
                  ("function" != typeof a.UNSAFE_componentWillReceiveProps &&
                    "function" != typeof a.componentWillReceiveProps) ||
                  ((l !== r || s !== u) && yi(t, a, r, u)),
                (ii = !1),
                (s = t.memoizedState),
                (a.state = s),
                fi(t, r, a, o),
                (d = t.memoizedState),
                l !== r || s !== d || po.current || ii
                  ? ("function" == typeof c &&
                      (hi(t, n, c, r), (d = t.memoizedState)),
                    (c = ii || gi(t, n, l, r, s, d, u))
                      ? (f ||
                          ("function" != typeof a.UNSAFE_componentWillUpdate &&
                            "function" != typeof a.componentWillUpdate) ||
                          ("function" == typeof a.componentWillUpdate &&
                            a.componentWillUpdate(r, d, u),
                          "function" == typeof a.UNSAFE_componentWillUpdate &&
                            a.UNSAFE_componentWillUpdate(r, d, u)),
                        "function" == typeof a.componentDidUpdate &&
                          (t.effectTag |= 4),
                        "function" == typeof a.getSnapshotBeforeUpdate &&
                          (t.effectTag |= 256))
                      : ("function" != typeof a.componentDidUpdate ||
                          (l === e.memoizedProps && s === e.memoizedState) ||
                          (t.effectTag |= 4),
                        "function" != typeof a.getSnapshotBeforeUpdate ||
                          (l === e.memoizedProps && s === e.memoizedState) ||
                          (t.effectTag |= 256),
                        (t.memoizedProps = r),
                        (t.memoizedState = d)),
                    (a.props = r),
                    (a.state = d),
                    (a.context = u),
                    (r = c))
                  : ("function" != typeof a.componentDidUpdate ||
                      (l === e.memoizedProps && s === e.memoizedState) ||
                      (t.effectTag |= 4),
                    "function" != typeof a.getSnapshotBeforeUpdate ||
                      (l === e.memoizedProps && s === e.memoizedState) ||
                      (t.effectTag |= 256),
                    (r = !1));
            return za(e, t, n, r, i, o);
          }
          function za(e, t, n, r, o, i) {
            Fa(e, t);
            var a = 0 != (64 & t.effectTag);
            if (!r && !a) return o && xo(t, n, !1), Ga(e, t, i);
            (r = t.stateNode), (Ca.current = t);
            var l =
              a && "function" != typeof n.getDerivedStateFromError
                ? null
                : r.render();
            return (
              (t.effectTag |= 1),
              null !== e && a
                ? ((t.child = Si(t, e.child, null, i)),
                  (t.child = Si(t, null, l, i)))
                : Na(e, t, l, i),
              (t.memoizedState = r.state),
              o && xo(t, n, !0),
              t.child
            );
          }
          function Da(e) {
            var t = e.stateNode;
            t.pendingContext
              ? vo(0, t.pendingContext, t.pendingContext !== t.context)
              : t.context && vo(0, t.context, !1),
              Ai(e, t.containerInfo);
          }
          var Ba,
            Ua,
            Wa,
            Va = { dehydrated: null, retryTime: 0 };
          function Ha(e, t, n) {
            var r,
              o = t.mode,
              i = t.pendingProps,
              a = Ii.current,
              l = !1;
            if (
              ((r = 0 != (64 & t.effectTag)) ||
                (r = 0 != (2 & a) && (null === e || null !== e.memoizedState)),
              r
                ? ((l = !0), (t.effectTag &= -65))
                : (null !== e && null === e.memoizedState) ||
                  void 0 === i.fallback ||
                  !0 === i.unstable_avoidThisFallback ||
                  (a |= 1),
              uo(Ii, 1 & a),
              null === e)
            ) {
              if ((void 0 !== i.fallback && Sa(t), l)) {
                if (
                  ((l = i.fallback),
                  ((i = Ps(null, o, 0, null)).return = t),
                  0 == (2 & t.mode))
                )
                  for (
                    e = null !== t.memoizedState ? t.child.child : t.child,
                      i.child = e;
                    null !== e;

                  )
                    (e.return = i), (e = e.sibling);
                return (
                  ((n = Ps(l, o, n, null)).return = t),
                  (i.sibling = n),
                  (t.memoizedState = Va),
                  (t.child = i),
                  n
                );
              }
              return (
                (o = i.children),
                (t.memoizedState = null),
                (t.child = Ti(t, null, o, n))
              );
            }
            if (null !== e.memoizedState) {
              if (((o = (e = e.child).sibling), l)) {
                if (
                  ((i = i.fallback),
                  ((n = Ts(e, e.pendingProps)).return = t),
                  0 == (2 & t.mode) &&
                    (l = null !== t.memoizedState ? t.child.child : t.child) !==
                      e.child)
                )
                  for (n.child = l; null !== l; )
                    (l.return = n), (l = l.sibling);
                return (
                  ((o = Ts(o, i)).return = t),
                  (n.sibling = o),
                  (n.childExpirationTime = 0),
                  (t.memoizedState = Va),
                  (t.child = n),
                  o
                );
              }
              return (
                (n = Si(t, e.child, i.children, n)),
                (t.memoizedState = null),
                (t.child = n)
              );
            }
            if (((e = e.child), l)) {
              if (
                ((l = i.fallback),
                ((i = Ps(null, o, 0, null)).return = t),
                (i.child = e),
                null !== e && (e.return = i),
                0 == (2 & t.mode))
              )
                for (
                  e = null !== t.memoizedState ? t.child.child : t.child,
                    i.child = e;
                  null !== e;

                )
                  (e.return = i), (e = e.sibling);
              return (
                ((n = Ps(l, o, n, null)).return = t),
                (i.sibling = n),
                (n.effectTag |= 2),
                (i.childExpirationTime = 0),
                (t.memoizedState = Va),
                (t.child = i),
                n
              );
            }
            return (
              (t.memoizedState = null), (t.child = Si(t, e, i.children, n))
            );
          }
          function qa(e, t) {
            e.expirationTime < t && (e.expirationTime = t);
            var n = e.alternate;
            null !== n && n.expirationTime < t && (n.expirationTime = t),
              ni(e.return, t);
          }
          function Qa(e, t, n, r, o, i) {
            var a = e.memoizedState;
            null === a
              ? (e.memoizedState = {
                  isBackwards: t,
                  rendering: null,
                  renderingStartTime: 0,
                  last: r,
                  tail: n,
                  tailExpiration: 0,
                  tailMode: o,
                  lastEffect: i,
                })
              : ((a.isBackwards = t),
                (a.rendering = null),
                (a.renderingStartTime = 0),
                (a.last = r),
                (a.tail = n),
                (a.tailExpiration = 0),
                (a.tailMode = o),
                (a.lastEffect = i));
          }
          function Ka(e, t, n) {
            var r = t.pendingProps,
              o = r.revealOrder,
              i = r.tail;
            if ((Na(e, t, r.children, n), 0 != (2 & (r = Ii.current))))
              (r = (1 & r) | 2), (t.effectTag |= 64);
            else {
              if (null !== e && 0 != (64 & e.effectTag))
                e: for (e = t.child; null !== e; ) {
                  if (13 === e.tag) null !== e.memoizedState && qa(e, n);
                  else if (19 === e.tag) qa(e, n);
                  else if (null !== e.child) {
                    (e.child.return = e), (e = e.child);
                    continue;
                  }
                  if (e === t) break e;
                  for (; null === e.sibling; ) {
                    if (null === e.return || e.return === t) break e;
                    e = e.return;
                  }
                  (e.sibling.return = e.return), (e = e.sibling);
                }
              r &= 1;
            }
            if ((uo(Ii, r), 0 == (2 & t.mode))) t.memoizedState = null;
            else
              switch (o) {
                case "forwards":
                  for (n = t.child, o = null; null !== n; )
                    null !== (e = n.alternate) && null === Li(e) && (o = n),
                      (n = n.sibling);
                  null === (n = o)
                    ? ((o = t.child), (t.child = null))
                    : ((o = n.sibling), (n.sibling = null)),
                    Qa(t, !1, o, n, i, t.lastEffect);
                  break;
                case "backwards":
                  for (n = null, o = t.child, t.child = null; null !== o; ) {
                    if (null !== (e = o.alternate) && null === Li(e)) {
                      t.child = o;
                      break;
                    }
                    (e = o.sibling), (o.sibling = n), (n = o), (o = e);
                  }
                  Qa(t, !0, n, null, i, t.lastEffect);
                  break;
                case "together":
                  Qa(t, !1, null, null, void 0, t.lastEffect);
                  break;
                default:
                  t.memoizedState = null;
              }
            return t.child;
          }
          function Ga(e, t, n) {
            null !== e && (t.dependencies = e.dependencies);
            var r = t.expirationTime;
            if ((0 !== r && as(r), t.childExpirationTime < n)) return null;
            if (null !== e && t.child !== e.child) throw Error(a(153));
            if (null !== t.child) {
              for (
                n = Ts((e = t.child), e.pendingProps),
                  t.child = n,
                  n.return = t;
                null !== e.sibling;

              )
                (e = e.sibling),
                  ((n = n.sibling = Ts(e, e.pendingProps)).return = t);
              n.sibling = null;
            }
            return t.child;
          }
          function $a(e, t) {
            switch (e.tailMode) {
              case "hidden":
                t = e.tail;
                for (var n = null; null !== t; )
                  null !== t.alternate && (n = t), (t = t.sibling);
                null === n ? (e.tail = null) : (n.sibling = null);
                break;
              case "collapsed":
                n = e.tail;
                for (var r = null; null !== n; )
                  null !== n.alternate && (r = n), (n = n.sibling);
                null === r
                  ? t || null === e.tail
                    ? (e.tail = null)
                    : (e.tail.sibling = null)
                  : (r.sibling = null);
            }
          }
          function Ya(e, t, n) {
            var r = t.pendingProps;
            switch (t.tag) {
              case 2:
              case 16:
              case 15:
              case 0:
              case 11:
              case 7:
              case 8:
              case 12:
              case 9:
              case 14:
                return null;
              case 1:
              case 17:
                return bo(t.type) && go(), null;
              case 3:
                return (
                  ji(),
                  so(po),
                  so(fo),
                  (n = t.stateNode).pendingContext &&
                    ((n.context = n.pendingContext), (n.pendingContext = null)),
                  (null !== e && null !== e.child) ||
                    !Oa(t) ||
                    (t.effectTag |= 4),
                  null
                );
              case 5:
                Fi(t), (n = Ni(Mi.current));
                var i = t.type;
                if (null !== e && null != t.stateNode)
                  Ua(e, t, i, r, n), e.ref !== t.ref && (t.effectTag |= 128);
                else {
                  if (!r) {
                    if (null === t.stateNode) throw Error(a(166));
                    return null;
                  }
                  if (((e = Ni(Pi.current)), Oa(t))) {
                    (r = t.stateNode), (i = t.type);
                    var l = t.memoizedProps;
                    switch (((r[Sn] = t), (r[Tn] = l), i)) {
                      case "iframe":
                      case "object":
                      case "embed":
                        qt("load", r);
                        break;
                      case "video":
                      case "audio":
                        for (e = 0; e < $e.length; e++) qt($e[e], r);
                        break;
                      case "source":
                        qt("error", r);
                        break;
                      case "img":
                      case "image":
                      case "link":
                        qt("error", r), qt("load", r);
                        break;
                      case "form":
                        qt("reset", r), qt("submit", r);
                        break;
                      case "details":
                        qt("toggle", r);
                        break;
                      case "input":
                        Ee(r, l), qt("invalid", r), an(n, "onChange");
                        break;
                      case "select":
                        (r._wrapperState = { wasMultiple: !!l.multiple }),
                          qt("invalid", r),
                          an(n, "onChange");
                        break;
                      case "textarea":
                        Ne(r, l), qt("invalid", r), an(n, "onChange");
                    }
                    for (var s in (nn(i, l), (e = null), l))
                      if (l.hasOwnProperty(s)) {
                        var u = l[s];
                        "children" === s
                          ? "string" == typeof u
                            ? r.textContent !== u && (e = ["children", u])
                            : "number" == typeof u &&
                              r.textContent !== "" + u &&
                              (e = ["children", "" + u])
                          : _.hasOwnProperty(s) && null != u && an(n, s);
                      }
                    switch (i) {
                      case "input":
                        we(r), Te(r, l, !0);
                        break;
                      case "textarea":
                        we(r), je(r);
                        break;
                      case "select":
                      case "option":
                        break;
                      default:
                        "function" == typeof l.onClick && (r.onclick = ln);
                    }
                    (n = e),
                      (t.updateQueue = n),
                      null !== n && (t.effectTag |= 4);
                  } else {
                    switch (
                      ((s = 9 === n.nodeType ? n : n.ownerDocument),
                      e === on && (e = Re(i)),
                      e === on
                        ? "script" === i
                          ? (((e = s.createElement("div")).innerHTML =
                              "<script></script>"),
                            (e = e.removeChild(e.firstChild)))
                          : "string" == typeof r.is
                          ? (e = s.createElement(i, { is: r.is }))
                          : ((e = s.createElement(i)),
                            "select" === i &&
                              ((s = e),
                              r.multiple
                                ? (s.multiple = !0)
                                : r.size && (s.size = r.size)))
                        : (e = s.createElementNS(e, i)),
                      (e[Sn] = t),
                      (e[Tn] = r),
                      Ba(e, t),
                      (t.stateNode = e),
                      (s = rn(i, r)),
                      i)
                    ) {
                      case "iframe":
                      case "object":
                      case "embed":
                        qt("load", e), (u = r);
                        break;
                      case "video":
                      case "audio":
                        for (u = 0; u < $e.length; u++) qt($e[u], e);
                        u = r;
                        break;
                      case "source":
                        qt("error", e), (u = r);
                        break;
                      case "img":
                      case "image":
                      case "link":
                        qt("error", e), qt("load", e), (u = r);
                        break;
                      case "form":
                        qt("reset", e), qt("submit", e), (u = r);
                        break;
                      case "details":
                        qt("toggle", e), (u = r);
                        break;
                      case "input":
                        Ee(e, r),
                          (u = ke(e, r)),
                          qt("invalid", e),
                          an(n, "onChange");
                        break;
                      case "option":
                        u = Pe(e, r);
                        break;
                      case "select":
                        (e._wrapperState = { wasMultiple: !!r.multiple }),
                          (u = o({}, r, { value: void 0 })),
                          qt("invalid", e),
                          an(n, "onChange");
                        break;
                      case "textarea":
                        Ne(e, r),
                          (u = Me(e, r)),
                          qt("invalid", e),
                          an(n, "onChange");
                        break;
                      default:
                        u = r;
                    }
                    nn(i, u);
                    var c = u;
                    for (l in c)
                      if (c.hasOwnProperty(l)) {
                        var f = c[l];
                        "style" === l
                          ? en(e, f)
                          : "dangerouslySetInnerHTML" === l
                          ? null != (f = f ? f.__html : void 0) && ze(e, f)
                          : "children" === l
                          ? "string" == typeof f
                            ? ("textarea" !== i || "" !== f) && De(e, f)
                            : "number" == typeof f && De(e, "" + f)
                          : "suppressContentEditableWarning" !== l &&
                            "suppressHydrationWarning" !== l &&
                            "autoFocus" !== l &&
                            (_.hasOwnProperty(l)
                              ? null != f && an(n, l)
                              : null != f && X(e, l, f, s));
                      }
                    switch (i) {
                      case "input":
                        we(e), Te(e, r, !1);
                        break;
                      case "textarea":
                        we(e), je(e);
                        break;
                      case "option":
                        null != r.value &&
                          e.setAttribute("value", "" + ve(r.value));
                        break;
                      case "select":
                        (e.multiple = !!r.multiple),
                          null != (n = r.value)
                            ? Ce(e, !!r.multiple, n, !1)
                            : null != r.defaultValue &&
                              Ce(e, !!r.multiple, r.defaultValue, !0);
                        break;
                      default:
                        "function" == typeof u.onClick && (e.onclick = ln);
                    }
                    vn(i, r) && (t.effectTag |= 4);
                  }
                  null !== t.ref && (t.effectTag |= 128);
                }
                return null;
              case 6:
                if (e && null != t.stateNode) Wa(0, t, e.memoizedProps, r);
                else {
                  if ("string" != typeof r && null === t.stateNode)
                    throw Error(a(166));
                  (n = Ni(Mi.current)),
                    Ni(Pi.current),
                    Oa(t)
                      ? ((n = t.stateNode),
                        (r = t.memoizedProps),
                        (n[Sn] = t),
                        n.nodeValue !== r && (t.effectTag |= 4))
                      : (((n = (9 === n.nodeType
                          ? n
                          : n.ownerDocument
                        ).createTextNode(r))[Sn] = t),
                        (t.stateNode = n));
                }
                return null;
              case 13:
                return (
                  so(Ii),
                  (r = t.memoizedState),
                  0 != (64 & t.effectTag)
                    ? ((t.expirationTime = n), t)
                    : ((n = null !== r),
                      (r = !1),
                      null === e
                        ? void 0 !== t.memoizedProps.fallback && Oa(t)
                        : ((r = null !== (i = e.memoizedState)),
                          n ||
                            null === i ||
                            (null !== (i = e.child.sibling) &&
                              (null !== (l = t.firstEffect)
                                ? ((t.firstEffect = i), (i.nextEffect = l))
                                : ((t.firstEffect = t.lastEffect = i),
                                  (i.nextEffect = null)),
                              (i.effectTag = 8)))),
                      n &&
                        !r &&
                        0 != (2 & t.mode) &&
                        ((null === e &&
                          !0 !== t.memoizedProps.unstable_avoidThisFallback) ||
                        0 != (1 & Ii.current)
                          ? Cl === kl && (Cl = El)
                          : ((Cl !== kl && Cl !== El) || (Cl = _l),
                            0 !== Rl &&
                              null !== Tl &&
                              (js(Tl, Pl), Rs(Tl, Rl)))),
                      (n || r) && (t.effectTag |= 4),
                      null)
                );
              case 4:
                return ji(), null;
              case 10:
                return ti(t), null;
              case 19:
                if ((so(Ii), null === (r = t.memoizedState))) return null;
                if (
                  ((i = 0 != (64 & t.effectTag)), null === (l = r.rendering))
                ) {
                  if (i) $a(r, !1);
                  else if (Cl !== kl || (null !== e && 0 != (64 & e.effectTag)))
                    for (l = t.child; null !== l; ) {
                      if (null !== (e = Li(l))) {
                        for (
                          t.effectTag |= 64,
                            $a(r, !1),
                            null !== (i = e.updateQueue) &&
                              ((t.updateQueue = i), (t.effectTag |= 4)),
                            null === r.lastEffect && (t.firstEffect = null),
                            t.lastEffect = r.lastEffect,
                            r = t.child;
                          null !== r;

                        )
                          (l = n),
                            ((i = r).effectTag &= 2),
                            (i.nextEffect = null),
                            (i.firstEffect = null),
                            (i.lastEffect = null),
                            null === (e = i.alternate)
                              ? ((i.childExpirationTime = 0),
                                (i.expirationTime = l),
                                (i.child = null),
                                (i.memoizedProps = null),
                                (i.memoizedState = null),
                                (i.updateQueue = null),
                                (i.dependencies = null))
                              : ((i.childExpirationTime =
                                  e.childExpirationTime),
                                (i.expirationTime = e.expirationTime),
                                (i.child = e.child),
                                (i.memoizedProps = e.memoizedProps),
                                (i.memoizedState = e.memoizedState),
                                (i.updateQueue = e.updateQueue),
                                (l = e.dependencies),
                                (i.dependencies =
                                  null === l
                                    ? null
                                    : {
                                        expirationTime: l.expirationTime,
                                        firstContext: l.firstContext,
                                        responders: l.responders,
                                      })),
                            (r = r.sibling);
                        return uo(Ii, (1 & Ii.current) | 2), t.child;
                      }
                      l = l.sibling;
                    }
                } else {
                  if (!i)
                    if (null !== (e = Li(l))) {
                      if (
                        ((t.effectTag |= 64),
                        (i = !0),
                        null !== (n = e.updateQueue) &&
                          ((t.updateQueue = n), (t.effectTag |= 4)),
                        $a(r, !0),
                        null === r.tail &&
                          "hidden" === r.tailMode &&
                          !l.alternate)
                      )
                        return (
                          null !== (t = t.lastEffect = r.lastEffect) &&
                            (t.nextEffect = null),
                          null
                        );
                    } else
                      2 * Bo() - r.renderingStartTime > r.tailExpiration &&
                        1 < n &&
                        ((t.effectTag |= 64),
                        (i = !0),
                        $a(r, !1),
                        (t.expirationTime = t.childExpirationTime = n - 1));
                  r.isBackwards
                    ? ((l.sibling = t.child), (t.child = l))
                    : (null !== (n = r.last) ? (n.sibling = l) : (t.child = l),
                      (r.last = l));
                }
                return null !== r.tail
                  ? (0 === r.tailExpiration && (r.tailExpiration = Bo() + 500),
                    (n = r.tail),
                    (r.rendering = n),
                    (r.tail = n.sibling),
                    (r.lastEffect = t.lastEffect),
                    (r.renderingStartTime = Bo()),
                    (n.sibling = null),
                    (t = Ii.current),
                    uo(Ii, i ? (1 & t) | 2 : 1 & t),
                    n)
                  : null;
            }
            throw Error(a(156, t.tag));
          }
          function Xa(e) {
            switch (e.tag) {
              case 1:
                bo(e.type) && go();
                var t = e.effectTag;
                return 4096 & t ? ((e.effectTag = (-4097 & t) | 64), e) : null;
              case 3:
                if ((ji(), so(po), so(fo), 0 != (64 & (t = e.effectTag))))
                  throw Error(a(285));
                return (e.effectTag = (-4097 & t) | 64), e;
              case 5:
                return Fi(e), null;
              case 13:
                return (
                  so(Ii),
                  4096 & (t = e.effectTag)
                    ? ((e.effectTag = (-4097 & t) | 64), e)
                    : null
                );
              case 19:
                return so(Ii), null;
              case 4:
                return ji(), null;
              case 10:
                return ti(e), null;
              default:
                return null;
            }
          }
          function Za(e, t) {
            return { value: e, source: t, stack: ge(t) };
          }
          (Ba = function (e, t) {
            for (var n = t.child; null !== n; ) {
              if (5 === n.tag || 6 === n.tag) e.appendChild(n.stateNode);
              else if (4 !== n.tag && null !== n.child) {
                (n.child.return = n), (n = n.child);
                continue;
              }
              if (n === t) break;
              for (; null === n.sibling; ) {
                if (null === n.return || n.return === t) return;
                n = n.return;
              }
              (n.sibling.return = n.return), (n = n.sibling);
            }
          }),
            (Ua = function (e, t, n, r, i) {
              var a = e.memoizedProps;
              if (a !== r) {
                var l,
                  s,
                  u = t.stateNode;
                switch ((Ni(Pi.current), (e = null), n)) {
                  case "input":
                    (a = ke(u, a)), (r = ke(u, r)), (e = []);
                    break;
                  case "option":
                    (a = Pe(u, a)), (r = Pe(u, r)), (e = []);
                    break;
                  case "select":
                    (a = o({}, a, { value: void 0 })),
                      (r = o({}, r, { value: void 0 })),
                      (e = []);
                    break;
                  case "textarea":
                    (a = Me(u, a)), (r = Me(u, r)), (e = []);
                    break;
                  default:
                    "function" != typeof a.onClick &&
                      "function" == typeof r.onClick &&
                      (u.onclick = ln);
                }
                for (l in (nn(n, r), (n = null), a))
                  if (
                    !r.hasOwnProperty(l) &&
                    a.hasOwnProperty(l) &&
                    null != a[l]
                  )
                    if ("style" === l)
                      for (s in (u = a[l]))
                        u.hasOwnProperty(s) && (n || (n = {}), (n[s] = ""));
                    else
                      "dangerouslySetInnerHTML" !== l &&
                        "children" !== l &&
                        "suppressContentEditableWarning" !== l &&
                        "suppressHydrationWarning" !== l &&
                        "autoFocus" !== l &&
                        (_.hasOwnProperty(l)
                          ? e || (e = [])
                          : (e = e || []).push(l, null));
                for (l in r) {
                  var c = r[l];
                  if (
                    ((u = null != a ? a[l] : void 0),
                    r.hasOwnProperty(l) && c !== u && (null != c || null != u))
                  )
                    if ("style" === l)
                      if (u) {
                        for (s in u)
                          !u.hasOwnProperty(s) ||
                            (c && c.hasOwnProperty(s)) ||
                            (n || (n = {}), (n[s] = ""));
                        for (s in c)
                          c.hasOwnProperty(s) &&
                            u[s] !== c[s] &&
                            (n || (n = {}), (n[s] = c[s]));
                      } else n || (e || (e = []), e.push(l, n)), (n = c);
                    else
                      "dangerouslySetInnerHTML" === l
                        ? ((c = c ? c.__html : void 0),
                          (u = u ? u.__html : void 0),
                          null != c && u !== c && (e = e || []).push(l, c))
                        : "children" === l
                        ? u === c ||
                          ("string" != typeof c && "number" != typeof c) ||
                          (e = e || []).push(l, "" + c)
                        : "suppressContentEditableWarning" !== l &&
                          "suppressHydrationWarning" !== l &&
                          (_.hasOwnProperty(l)
                            ? (null != c && an(i, l), e || u === c || (e = []))
                            : (e = e || []).push(l, c));
                }
                n && (e = e || []).push("style", n),
                  (i = e),
                  (t.updateQueue = i) && (t.effectTag |= 4);
              }
            }),
            (Wa = function (e, t, n, r) {
              n !== r && (t.effectTag |= 4);
            });
          var Ja = "function" == typeof WeakSet ? WeakSet : Set;
          function el(e, t) {
            var n = t.source,
              r = t.stack;
            null === r && null !== n && (r = ge(n)),
              null !== n && be(n.type),
              (t = t.value),
              null !== e && 1 === e.tag && be(e.type);
            try {
              console.error(t);
            } catch (e) {
              setTimeout(function () {
                throw e;
              });
            }
          }
          function tl(e) {
            var t = e.ref;
            if (null !== t)
              if ("function" == typeof t)
                try {
                  t(null);
                } catch (t) {
                  vs(e, t);
                }
              else t.current = null;
          }
          function nl(e, t) {
            switch (t.tag) {
              case 0:
              case 11:
              case 15:
              case 22:
              case 3:
              case 5:
              case 6:
              case 4:
              case 17:
                return;
              case 1:
                if (256 & t.effectTag && null !== e) {
                  var n = e.memoizedProps,
                    r = e.memoizedState;
                  (t = (e = t.stateNode).getSnapshotBeforeUpdate(
                    t.elementType === t.type ? n : $o(t.type, n),
                    r
                  )),
                    (e.__reactInternalSnapshotBeforeUpdate = t);
                }
                return;
            }
            throw Error(a(163));
          }
          function rl(e, t) {
            if (
              null !== (t = null !== (t = t.updateQueue) ? t.lastEffect : null)
            ) {
              var n = (t = t.next);
              do {
                if ((n.tag & e) === e) {
                  var r = n.destroy;
                  (n.destroy = void 0), void 0 !== r && r();
                }
                n = n.next;
              } while (n !== t);
            }
          }
          function ol(e, t) {
            if (
              null !== (t = null !== (t = t.updateQueue) ? t.lastEffect : null)
            ) {
              var n = (t = t.next);
              do {
                if ((n.tag & e) === e) {
                  var r = n.create;
                  n.destroy = r();
                }
                n = n.next;
              } while (n !== t);
            }
          }
          function il(e, t, n) {
            switch (n.tag) {
              case 0:
              case 11:
              case 15:
              case 22:
                return void ol(3, n);
              case 1:
                if (((e = n.stateNode), 4 & n.effectTag))
                  if (null === t) e.componentDidMount();
                  else {
                    var r =
                      n.elementType === n.type
                        ? t.memoizedProps
                        : $o(n.type, t.memoizedProps);
                    e.componentDidUpdate(
                      r,
                      t.memoizedState,
                      e.__reactInternalSnapshotBeforeUpdate
                    );
                  }
                return void (null !== (t = n.updateQueue) && di(n, t, e));
              case 3:
                if (null !== (t = n.updateQueue)) {
                  if (((e = null), null !== n.child))
                    switch (n.child.tag) {
                      case 5:
                      case 1:
                        e = n.child.stateNode;
                    }
                  di(n, t, e);
                }
                return;
              case 5:
                return (
                  (e = n.stateNode),
                  void (
                    null === t &&
                    4 & n.effectTag &&
                    vn(n.type, n.memoizedProps) &&
                    e.focus()
                  )
                );
              case 6:
              case 4:
              case 12:
              case 19:
              case 17:
              case 20:
              case 21:
                return;
              case 13:
                return void (
                  null === n.memoizedState &&
                  ((n = n.alternate),
                  null !== n &&
                    ((n = n.memoizedState),
                    null !== n && ((n = n.dehydrated), null !== n && Rt(n))))
                );
            }
            throw Error(a(163));
          }
          function al(e, t, n) {
            switch (("function" == typeof ks && ks(t), t.tag)) {
              case 0:
              case 11:
              case 14:
              case 15:
              case 22:
                if (
                  null !== (e = t.updateQueue) &&
                  null !== (e = e.lastEffect)
                ) {
                  var r = e.next;
                  Vo(97 < n ? 97 : n, function () {
                    var e = r;
                    do {
                      var n = e.destroy;
                      if (void 0 !== n) {
                        var o = t;
                        try {
                          n();
                        } catch (e) {
                          vs(o, e);
                        }
                      }
                      e = e.next;
                    } while (e !== r);
                  });
                }
                break;
              case 1:
                tl(t),
                  "function" == typeof (n = t.stateNode).componentWillUnmount &&
                    (function (e, t) {
                      try {
                        (t.props = e.memoizedProps),
                          (t.state = e.memoizedState),
                          t.componentWillUnmount();
                      } catch (t) {
                        vs(e, t);
                      }
                    })(t, n);
                break;
              case 5:
                tl(t);
                break;
              case 4:
                dl(e, t, n);
            }
          }
          function ll(e) {
            var t = e.alternate;
            (e.return = null),
              (e.child = null),
              (e.memoizedState = null),
              (e.updateQueue = null),
              (e.dependencies = null),
              (e.alternate = null),
              (e.firstEffect = null),
              (e.lastEffect = null),
              (e.pendingProps = null),
              (e.memoizedProps = null),
              (e.stateNode = null),
              null !== t && ll(t);
          }
          function sl(e) {
            return 5 === e.tag || 3 === e.tag || 4 === e.tag;
          }
          function ul(e) {
            e: {
              for (var t = e.return; null !== t; ) {
                if (sl(t)) {
                  var n = t;
                  break e;
                }
                t = t.return;
              }
              throw Error(a(160));
            }
            switch (((t = n.stateNode), n.tag)) {
              case 5:
                var r = !1;
                break;
              case 3:
              case 4:
                (t = t.containerInfo), (r = !0);
                break;
              default:
                throw Error(a(161));
            }
            16 & n.effectTag && (De(t, ""), (n.effectTag &= -17));
            e: t: for (n = e; ; ) {
              for (; null === n.sibling; ) {
                if (null === n.return || sl(n.return)) {
                  n = null;
                  break e;
                }
                n = n.return;
              }
              for (
                n.sibling.return = n.return, n = n.sibling;
                5 !== n.tag && 6 !== n.tag && 18 !== n.tag;

              ) {
                if (2 & n.effectTag) continue t;
                if (null === n.child || 4 === n.tag) continue t;
                (n.child.return = n), (n = n.child);
              }
              if (!(2 & n.effectTag)) {
                n = n.stateNode;
                break e;
              }
            }
            r ? cl(e, n, t) : fl(e, n, t);
          }
          function cl(e, t, n) {
            var r = e.tag,
              o = 5 === r || 6 === r;
            if (o)
              (e = o ? e.stateNode : e.stateNode.instance),
                t
                  ? 8 === n.nodeType
                    ? n.parentNode.insertBefore(e, t)
                    : n.insertBefore(e, t)
                  : (8 === n.nodeType
                      ? (t = n.parentNode).insertBefore(e, n)
                      : (t = n).appendChild(e),
                    null != (n = n._reactRootContainer) ||
                      null !== t.onclick ||
                      (t.onclick = ln));
            else if (4 !== r && null !== (e = e.child))
              for (cl(e, t, n), e = e.sibling; null !== e; )
                cl(e, t, n), (e = e.sibling);
          }
          function fl(e, t, n) {
            var r = e.tag,
              o = 5 === r || 6 === r;
            if (o)
              (e = o ? e.stateNode : e.stateNode.instance),
                t ? n.insertBefore(e, t) : n.appendChild(e);
            else if (4 !== r && null !== (e = e.child))
              for (fl(e, t, n), e = e.sibling; null !== e; )
                fl(e, t, n), (e = e.sibling);
          }
          function dl(e, t, n) {
            for (var r, o, i = t, l = !1; ; ) {
              if (!l) {
                l = i.return;
                e: for (;;) {
                  if (null === l) throw Error(a(160));
                  switch (((r = l.stateNode), l.tag)) {
                    case 5:
                      o = !1;
                      break e;
                    case 3:
                    case 4:
                      (r = r.containerInfo), (o = !0);
                      break e;
                  }
                  l = l.return;
                }
                l = !0;
              }
              if (5 === i.tag || 6 === i.tag) {
                e: for (var s = e, u = i, c = n, f = u; ; )
                  if ((al(s, f, c), null !== f.child && 4 !== f.tag))
                    (f.child.return = f), (f = f.child);
                  else {
                    if (f === u) break e;
                    for (; null === f.sibling; ) {
                      if (null === f.return || f.return === u) break e;
                      f = f.return;
                    }
                    (f.sibling.return = f.return), (f = f.sibling);
                  }
                o
                  ? ((s = r),
                    (u = i.stateNode),
                    8 === s.nodeType
                      ? s.parentNode.removeChild(u)
                      : s.removeChild(u))
                  : r.removeChild(i.stateNode);
              } else if (4 === i.tag) {
                if (null !== i.child) {
                  (r = i.stateNode.containerInfo),
                    (o = !0),
                    (i.child.return = i),
                    (i = i.child);
                  continue;
                }
              } else if ((al(e, i, n), null !== i.child)) {
                (i.child.return = i), (i = i.child);
                continue;
              }
              if (i === t) break;
              for (; null === i.sibling; ) {
                if (null === i.return || i.return === t) return;
                4 === (i = i.return).tag && (l = !1);
              }
              (i.sibling.return = i.return), (i = i.sibling);
            }
          }
          function pl(e, t) {
            switch (t.tag) {
              case 0:
              case 11:
              case 14:
              case 15:
              case 22:
                return void rl(3, t);
              case 1:
              case 12:
              case 17:
                return;
              case 5:
                var n = t.stateNode;
                if (null != n) {
                  var r = t.memoizedProps,
                    o = null !== e ? e.memoizedProps : r;
                  e = t.type;
                  var i = t.updateQueue;
                  if (((t.updateQueue = null), null !== i)) {
                    for (
                      n[Tn] = r,
                        "input" === e &&
                          "radio" === r.type &&
                          null != r.name &&
                          _e(n, r),
                        rn(e, o),
                        t = rn(e, r),
                        o = 0;
                      o < i.length;
                      o += 2
                    ) {
                      var l = i[o],
                        s = i[o + 1];
                      "style" === l
                        ? en(n, s)
                        : "dangerouslySetInnerHTML" === l
                        ? ze(n, s)
                        : "children" === l
                        ? De(n, s)
                        : X(n, l, s, t);
                    }
                    switch (e) {
                      case "input":
                        Se(n, r);
                        break;
                      case "textarea":
                        Ae(n, r);
                        break;
                      case "select":
                        (t = n._wrapperState.wasMultiple),
                          (n._wrapperState.wasMultiple = !!r.multiple),
                          null != (e = r.value)
                            ? Ce(n, !!r.multiple, e, !1)
                            : t !== !!r.multiple &&
                              (null != r.defaultValue
                                ? Ce(n, !!r.multiple, r.defaultValue, !0)
                                : Ce(
                                    n,
                                    !!r.multiple,
                                    r.multiple ? [] : "",
                                    !1
                                  ));
                    }
                  }
                }
                return;
              case 6:
                if (null === t.stateNode) throw Error(a(162));
                return void (t.stateNode.nodeValue = t.memoizedProps);
              case 3:
                return void (
                  (t = t.stateNode).hydrate &&
                  ((t.hydrate = !1), Rt(t.containerInfo))
                );
              case 13:
                if (
                  ((n = t),
                  null === t.memoizedState
                    ? (r = !1)
                    : ((r = !0), (n = t.child), (Il = Bo())),
                  null !== n)
                )
                  e: for (e = n; ; ) {
                    if (5 === e.tag)
                      (i = e.stateNode),
                        r
                          ? "function" == typeof (i = i.style).setProperty
                            ? i.setProperty("display", "none", "important")
                            : (i.display = "none")
                          : ((i = e.stateNode),
                            (o =
                              null != (o = e.memoizedProps.style) &&
                              o.hasOwnProperty("display")
                                ? o.display
                                : null),
                            (i.style.display = Jt("display", o)));
                    else if (6 === e.tag)
                      e.stateNode.nodeValue = r ? "" : e.memoizedProps;
                    else {
                      if (
                        13 === e.tag &&
                        null !== e.memoizedState &&
                        null === e.memoizedState.dehydrated
                      ) {
                        ((i = e.child.sibling).return = e), (e = i);
                        continue;
                      }
                      if (null !== e.child) {
                        (e.child.return = e), (e = e.child);
                        continue;
                      }
                    }
                    if (e === n) break;
                    for (; null === e.sibling; ) {
                      if (null === e.return || e.return === n) break e;
                      e = e.return;
                    }
                    (e.sibling.return = e.return), (e = e.sibling);
                  }
                return void ml(t);
              case 19:
                return void ml(t);
            }
            throw Error(a(163));
          }
          function ml(e) {
            var t = e.updateQueue;
            if (null !== t) {
              e.updateQueue = null;
              var n = e.stateNode;
              null === n && (n = e.stateNode = new Ja()),
                t.forEach(function (t) {
                  var r = ws.bind(null, e, t);
                  n.has(t) || (n.add(t), t.then(r, r));
                });
            }
          }
          var hl = "function" == typeof WeakMap ? WeakMap : Map;
          function bl(e, t, n) {
            ((n = si(n, null)).tag = 3), (n.payload = { element: null });
            var r = t.value;
            return (
              (n.callback = function () {
                zl || ((zl = !0), (Dl = r)), el(e, t);
              }),
              n
            );
          }
          function gl(e, t, n) {
            (n = si(n, null)).tag = 3;
            var r = e.type.getDerivedStateFromError;
            if ("function" == typeof r) {
              var o = t.value;
              n.payload = function () {
                return el(e, t), r(o);
              };
            }
            var i = e.stateNode;
            return (
              null !== i &&
                "function" == typeof i.componentDidCatch &&
                (n.callback = function () {
                  "function" != typeof r &&
                    (null === Bl ? (Bl = new Set([this])) : Bl.add(this),
                    el(e, t));
                  var n = t.stack;
                  this.componentDidCatch(t.value, {
                    componentStack: null !== n ? n : "",
                  });
                }),
              n
            );
          }
          var vl,
            yl = Math.ceil,
            wl = Y.ReactCurrentDispatcher,
            xl = Y.ReactCurrentOwner,
            kl = 0,
            El = 3,
            _l = 4,
            Sl = 0,
            Tl = null,
            Ol = null,
            Pl = 0,
            Cl = kl,
            Ml = null,
            Nl = 1073741823,
            Al = 1073741823,
            jl = null,
            Rl = 0,
            Fl = !1,
            Il = 0,
            Ll = null,
            zl = !1,
            Dl = null,
            Bl = null,
            Ul = !1,
            Wl = null,
            Vl = 90,
            Hl = null,
            ql = 0,
            Ql = null,
            Kl = 0;
          function Gl() {
            return 0 != (48 & Sl)
              ? 1073741821 - ((Bo() / 10) | 0)
              : 0 !== Kl
              ? Kl
              : (Kl = 1073741821 - ((Bo() / 10) | 0));
          }
          function $l(e, t, n) {
            if (0 == (2 & (t = t.mode))) return 1073741823;
            var r = Uo();
            if (0 == (4 & t)) return 99 === r ? 1073741823 : 1073741822;
            if (0 != (16 & Sl)) return Pl;
            if (null !== n) e = Go(e, 0 | n.timeoutMs || 5e3, 250);
            else
              switch (r) {
                case 99:
                  e = 1073741823;
                  break;
                case 98:
                  e = Go(e, 150, 100);
                  break;
                case 97:
                case 96:
                  e = Go(e, 5e3, 250);
                  break;
                case 95:
                  e = 2;
                  break;
                default:
                  throw Error(a(326));
              }
            return null !== Tl && e === Pl && --e, e;
          }
          function Yl(e, t) {
            if (50 < ql) throw ((ql = 0), (Ql = null), Error(a(185)));
            if (null !== (e = Xl(e, t))) {
              var n = Uo();
              1073741823 === t
                ? 0 != (8 & Sl) && 0 == (48 & Sl)
                  ? ts(e)
                  : (Jl(e), 0 === Sl && Qo())
                : Jl(e),
                0 == (4 & Sl) ||
                  (98 !== n && 99 !== n) ||
                  (null === Hl
                    ? (Hl = new Map([[e, t]]))
                    : (void 0 === (n = Hl.get(e)) || n > t) && Hl.set(e, t));
            }
          }
          function Xl(e, t) {
            e.expirationTime < t && (e.expirationTime = t);
            var n = e.alternate;
            null !== n && n.expirationTime < t && (n.expirationTime = t);
            var r = e.return,
              o = null;
            if (null === r && 3 === e.tag) o = e.stateNode;
            else
              for (; null !== r; ) {
                if (
                  ((n = r.alternate),
                  r.childExpirationTime < t && (r.childExpirationTime = t),
                  null !== n &&
                    n.childExpirationTime < t &&
                    (n.childExpirationTime = t),
                  null === r.return && 3 === r.tag)
                ) {
                  o = r.stateNode;
                  break;
                }
                r = r.return;
              }
            return (
              null !== o &&
                (Tl === o && (as(t), Cl === _l && js(o, Pl)), Rs(o, t)),
              o
            );
          }
          function Zl(e) {
            var t = e.lastExpiredTime;
            if (0 !== t) return t;
            if (!As(e, (t = e.firstPendingTime))) return t;
            var n = e.lastPingedTime;
            return 2 >= (e = n > (e = e.nextKnownPendingLevel) ? n : e) &&
              t !== e
              ? 0
              : e;
          }
          function Jl(e) {
            if (0 !== e.lastExpiredTime)
              (e.callbackExpirationTime = 1073741823),
                (e.callbackPriority = 99),
                (e.callbackNode = qo(ts.bind(null, e)));
            else {
              var t = Zl(e),
                n = e.callbackNode;
              if (0 === t)
                null !== n &&
                  ((e.callbackNode = null),
                  (e.callbackExpirationTime = 0),
                  (e.callbackPriority = 90));
              else {
                var r = Gl();
                if (
                  ((r =
                    1073741823 === t
                      ? 99
                      : 1 === t || 2 === t
                      ? 95
                      : 0 >= (r = 10 * (1073741821 - t) - 10 * (1073741821 - r))
                      ? 99
                      : 250 >= r
                      ? 98
                      : 5250 >= r
                      ? 97
                      : 95),
                  null !== n)
                ) {
                  var o = e.callbackPriority;
                  if (e.callbackExpirationTime === t && o >= r) return;
                  n !== jo && _o(n);
                }
                (e.callbackExpirationTime = t),
                  (e.callbackPriority = r),
                  (t =
                    1073741823 === t
                      ? qo(ts.bind(null, e))
                      : Ho(r, es.bind(null, e), {
                          timeout: 10 * (1073741821 - t) - Bo(),
                        })),
                  (e.callbackNode = t);
              }
            }
          }
          function es(e, t) {
            if (((Kl = 0), t)) return Fs(e, (t = Gl())), Jl(e), null;
            var n = Zl(e);
            if (0 !== n) {
              if (((t = e.callbackNode), 0 != (48 & Sl))) throw Error(a(327));
              if ((hs(), (e === Tl && n === Pl) || ns(e, n), null !== Ol)) {
                var r = Sl;
                Sl |= 16;
                for (var o = os(); ; )
                  try {
                    ss();
                    break;
                  } catch (t) {
                    rs(e, t);
                  }
                if ((ei(), (Sl = r), (wl.current = o), 1 === Cl))
                  throw ((t = Ml), ns(e, n), js(e, n), Jl(e), t);
                if (null === Ol)
                  switch (
                    ((o = e.finishedWork = e.current.alternate),
                    (e.finishedExpirationTime = n),
                    (r = Cl),
                    (Tl = null),
                    r)
                  ) {
                    case kl:
                    case 1:
                      throw Error(a(345));
                    case 2:
                      Fs(e, 2 < n ? 2 : n);
                      break;
                    case El:
                      if (
                        (js(e, n),
                        n === (r = e.lastSuspendedTime) &&
                          (e.nextKnownPendingLevel = fs(o)),
                        1073741823 === Nl && 10 < (o = Il + 500 - Bo()))
                      ) {
                        if (Fl) {
                          var i = e.lastPingedTime;
                          if (0 === i || i >= n) {
                            (e.lastPingedTime = n), ns(e, n);
                            break;
                          }
                        }
                        if (0 !== (i = Zl(e)) && i !== n) break;
                        if (0 !== r && r !== n) {
                          e.lastPingedTime = r;
                          break;
                        }
                        e.timeoutHandle = wn(ds.bind(null, e), o);
                        break;
                      }
                      ds(e);
                      break;
                    case _l:
                      if (
                        (js(e, n),
                        n === (r = e.lastSuspendedTime) &&
                          (e.nextKnownPendingLevel = fs(o)),
                        Fl && (0 === (o = e.lastPingedTime) || o >= n))
                      ) {
                        (e.lastPingedTime = n), ns(e, n);
                        break;
                      }
                      if (0 !== (o = Zl(e)) && o !== n) break;
                      if (0 !== r && r !== n) {
                        e.lastPingedTime = r;
                        break;
                      }
                      if (
                        (1073741823 !== Al
                          ? (r = 10 * (1073741821 - Al) - Bo())
                          : 1073741823 === Nl
                          ? (r = 0)
                          : ((r = 10 * (1073741821 - Nl) - 5e3),
                            0 > (r = (o = Bo()) - r) && (r = 0),
                            (n = 10 * (1073741821 - n) - o) <
                              (r =
                                (120 > r
                                  ? 120
                                  : 480 > r
                                  ? 480
                                  : 1080 > r
                                  ? 1080
                                  : 1920 > r
                                  ? 1920
                                  : 3e3 > r
                                  ? 3e3
                                  : 4320 > r
                                  ? 4320
                                  : 1960 * yl(r / 1960)) - r) && (r = n)),
                        10 < r)
                      ) {
                        e.timeoutHandle = wn(ds.bind(null, e), r);
                        break;
                      }
                      ds(e);
                      break;
                    case 5:
                      if (1073741823 !== Nl && null !== jl) {
                        i = Nl;
                        var l = jl;
                        if (
                          (0 >= (r = 0 | l.busyMinDurationMs)
                            ? (r = 0)
                            : ((o = 0 | l.busyDelayMs),
                              (r =
                                (i =
                                  Bo() -
                                  (10 * (1073741821 - i) -
                                    (0 | l.timeoutMs || 5e3))) <= o
                                  ? 0
                                  : o + r - i)),
                          10 < r)
                        ) {
                          js(e, n), (e.timeoutHandle = wn(ds.bind(null, e), r));
                          break;
                        }
                      }
                      ds(e);
                      break;
                    default:
                      throw Error(a(329));
                  }
                if ((Jl(e), e.callbackNode === t)) return es.bind(null, e);
              }
            }
            return null;
          }
          function ts(e) {
            var t = e.lastExpiredTime;
            if (((t = 0 !== t ? t : 1073741823), 0 != (48 & Sl)))
              throw Error(a(327));
            if ((hs(), (e === Tl && t === Pl) || ns(e, t), null !== Ol)) {
              var n = Sl;
              Sl |= 16;
              for (var r = os(); ; )
                try {
                  ls();
                  break;
                } catch (t) {
                  rs(e, t);
                }
              if ((ei(), (Sl = n), (wl.current = r), 1 === Cl))
                throw ((n = Ml), ns(e, t), js(e, t), Jl(e), n);
              if (null !== Ol) throw Error(a(261));
              (e.finishedWork = e.current.alternate),
                (e.finishedExpirationTime = t),
                (Tl = null),
                ds(e),
                Jl(e);
            }
            return null;
          }
          function ns(e, t) {
            (e.finishedWork = null), (e.finishedExpirationTime = 0);
            var n = e.timeoutHandle;
            if ((-1 !== n && ((e.timeoutHandle = -1), xn(n)), null !== Ol))
              for (n = Ol.return; null !== n; ) {
                var r = n;
                switch (r.tag) {
                  case 1:
                    null != (r = r.type.childContextTypes) && go();
                    break;
                  case 3:
                    ji(), so(po), so(fo);
                    break;
                  case 5:
                    Fi(r);
                    break;
                  case 4:
                    ji();
                    break;
                  case 13:
                  case 19:
                    so(Ii);
                    break;
                  case 10:
                    ti(r);
                }
                n = n.return;
              }
            (Tl = e),
              (Ol = Ts(e.current, null)),
              (Pl = t),
              (Cl = kl),
              (Ml = null),
              (Al = Nl = 1073741823),
              (jl = null),
              (Rl = 0),
              (Fl = !1);
          }
          function rs(e, t) {
            for (;;) {
              try {
                if ((ei(), (Di.current = ba), qi))
                  for (var n = Wi.memoizedState; null !== n; ) {
                    var r = n.queue;
                    null !== r && (r.pending = null), (n = n.next);
                  }
                if (
                  ((Ui = 0),
                  (Hi = Vi = Wi = null),
                  (qi = !1),
                  null === Ol || null === Ol.return)
                )
                  return (Cl = 1), (Ml = t), (Ol = null);
                e: {
                  var o = e,
                    i = Ol.return,
                    a = Ol,
                    l = t;
                  if (
                    ((t = Pl),
                    (a.effectTag |= 2048),
                    (a.firstEffect = a.lastEffect = null),
                    null !== l &&
                      "object" == typeof l &&
                      "function" == typeof l.then)
                  ) {
                    var s = l;
                    if (0 == (2 & a.mode)) {
                      var u = a.alternate;
                      u
                        ? ((a.updateQueue = u.updateQueue),
                          (a.memoizedState = u.memoizedState),
                          (a.expirationTime = u.expirationTime))
                        : ((a.updateQueue = null), (a.memoizedState = null));
                    }
                    var c = 0 != (1 & Ii.current),
                      f = i;
                    do {
                      var d;
                      if ((d = 13 === f.tag)) {
                        var p = f.memoizedState;
                        if (null !== p) d = null !== p.dehydrated;
                        else {
                          var m = f.memoizedProps;
                          d =
                            void 0 !== m.fallback &&
                            (!0 !== m.unstable_avoidThisFallback || !c);
                        }
                      }
                      if (d) {
                        var h = f.updateQueue;
                        if (null === h) {
                          var b = new Set();
                          b.add(s), (f.updateQueue = b);
                        } else h.add(s);
                        if (0 == (2 & f.mode)) {
                          if (
                            ((f.effectTag |= 64),
                            (a.effectTag &= -2981),
                            1 === a.tag)
                          )
                            if (null === a.alternate) a.tag = 17;
                            else {
                              var g = si(1073741823, null);
                              (g.tag = 2), ui(a, g);
                            }
                          a.expirationTime = 1073741823;
                          break e;
                        }
                        (l = void 0), (a = t);
                        var v = o.pingCache;
                        if (
                          (null === v
                            ? ((v = o.pingCache = new hl()),
                              (l = new Set()),
                              v.set(s, l))
                            : void 0 === (l = v.get(s)) &&
                              ((l = new Set()), v.set(s, l)),
                          !l.has(a))
                        ) {
                          l.add(a);
                          var y = ys.bind(null, o, s, a);
                          s.then(y, y);
                        }
                        (f.effectTag |= 4096), (f.expirationTime = t);
                        break e;
                      }
                      f = f.return;
                    } while (null !== f);
                    l = Error(
                      (be(a.type) || "A React component") +
                        " suspended while rendering, but no fallback UI was specified.\n\nAdd a <Suspense fallback=...> component higher in the tree to provide a loading indicator or placeholder to display." +
                        ge(a)
                    );
                  }
                  5 !== Cl && (Cl = 2), (l = Za(l, a)), (f = i);
                  do {
                    switch (f.tag) {
                      case 3:
                        (s = l),
                          (f.effectTag |= 4096),
                          (f.expirationTime = t),
                          ci(f, bl(f, s, t));
                        break e;
                      case 1:
                        s = l;
                        var w = f.type,
                          x = f.stateNode;
                        if (
                          0 == (64 & f.effectTag) &&
                          ("function" == typeof w.getDerivedStateFromError ||
                            (null !== x &&
                              "function" == typeof x.componentDidCatch &&
                              (null === Bl || !Bl.has(x))))
                        ) {
                          (f.effectTag |= 4096),
                            (f.expirationTime = t),
                            ci(f, gl(f, s, t));
                          break e;
                        }
                    }
                    f = f.return;
                  } while (null !== f);
                }
                Ol = cs(Ol);
              } catch (e) {
                t = e;
                continue;
              }
              break;
            }
          }
          function os() {
            var e = wl.current;
            return (wl.current = ba), null === e ? ba : e;
          }
          function is(e, t) {
            e < Nl && 2 < e && (Nl = e),
              null !== t && e < Al && 2 < e && ((Al = e), (jl = t));
          }
          function as(e) {
            e > Rl && (Rl = e);
          }
          function ls() {
            for (; null !== Ol; ) Ol = us(Ol);
          }
          function ss() {
            for (; null !== Ol && !Ro(); ) Ol = us(Ol);
          }
          function us(e) {
            var t = vl(e.alternate, e, Pl);
            return (
              (e.memoizedProps = e.pendingProps),
              null === t && (t = cs(e)),
              (xl.current = null),
              t
            );
          }
          function cs(e) {
            Ol = e;
            do {
              var t = Ol.alternate;
              if (((e = Ol.return), 0 == (2048 & Ol.effectTag))) {
                if (
                  ((t = Ya(t, Ol, Pl)),
                  1 === Pl || 1 !== Ol.childExpirationTime)
                ) {
                  for (var n = 0, r = Ol.child; null !== r; ) {
                    var o = r.expirationTime,
                      i = r.childExpirationTime;
                    o > n && (n = o), i > n && (n = i), (r = r.sibling);
                  }
                  Ol.childExpirationTime = n;
                }
                if (null !== t) return t;
                null !== e &&
                  0 == (2048 & e.effectTag) &&
                  (null === e.firstEffect && (e.firstEffect = Ol.firstEffect),
                  null !== Ol.lastEffect &&
                    (null !== e.lastEffect &&
                      (e.lastEffect.nextEffect = Ol.firstEffect),
                    (e.lastEffect = Ol.lastEffect)),
                  1 < Ol.effectTag &&
                    (null !== e.lastEffect
                      ? (e.lastEffect.nextEffect = Ol)
                      : (e.firstEffect = Ol),
                    (e.lastEffect = Ol)));
              } else {
                if (null !== (t = Xa(Ol))) return (t.effectTag &= 2047), t;
                null !== e &&
                  ((e.firstEffect = e.lastEffect = null),
                  (e.effectTag |= 2048));
              }
              if (null !== (t = Ol.sibling)) return t;
              Ol = e;
            } while (null !== Ol);
            return Cl === kl && (Cl = 5), null;
          }
          function fs(e) {
            var t = e.expirationTime;
            return t > (e = e.childExpirationTime) ? t : e;
          }
          function ds(e) {
            var t = Uo();
            return Vo(99, ps.bind(null, e, t)), null;
          }
          function ps(e, t) {
            do {
              hs();
            } while (null !== Wl);
            if (0 != (48 & Sl)) throw Error(a(327));
            var n = e.finishedWork,
              r = e.finishedExpirationTime;
            if (null === n) return null;
            if (
              ((e.finishedWork = null),
              (e.finishedExpirationTime = 0),
              n === e.current)
            )
              throw Error(a(177));
            (e.callbackNode = null),
              (e.callbackExpirationTime = 0),
              (e.callbackPriority = 90),
              (e.nextKnownPendingLevel = 0);
            var o = fs(n);
            if (
              ((e.firstPendingTime = o),
              r <= e.lastSuspendedTime
                ? (e.firstSuspendedTime = e.lastSuspendedTime = e.nextKnownPendingLevel = 0)
                : r <= e.firstSuspendedTime && (e.firstSuspendedTime = r - 1),
              r <= e.lastPingedTime && (e.lastPingedTime = 0),
              r <= e.lastExpiredTime && (e.lastExpiredTime = 0),
              e === Tl && ((Ol = Tl = null), (Pl = 0)),
              1 < n.effectTag
                ? null !== n.lastEffect
                  ? ((n.lastEffect.nextEffect = n), (o = n.firstEffect))
                  : (o = n)
                : (o = n.firstEffect),
              null !== o)
            ) {
              var i = Sl;
              (Sl |= 32), (xl.current = null), (bn = Ht);
              var l = dn();
              if (pn(l)) {
                if ("selectionStart" in l)
                  var s = { start: l.selectionStart, end: l.selectionEnd };
                else
                  e: {
                    var u =
                      (s = ((s = l.ownerDocument) && s.defaultView) || window)
                        .getSelection && s.getSelection();
                    if (u && 0 !== u.rangeCount) {
                      s = u.anchorNode;
                      var c = u.anchorOffset,
                        f = u.focusNode;
                      u = u.focusOffset;
                      try {
                        s.nodeType, f.nodeType;
                      } catch (e) {
                        s = null;
                        break e;
                      }
                      var d = 0,
                        p = -1,
                        m = -1,
                        h = 0,
                        b = 0,
                        g = l,
                        v = null;
                      t: for (;;) {
                        for (
                          var y;
                          g !== s ||
                            (0 !== c && 3 !== g.nodeType) ||
                            (p = d + c),
                            g !== f ||
                              (0 !== u && 3 !== g.nodeType) ||
                              (m = d + u),
                            3 === g.nodeType && (d += g.nodeValue.length),
                            null !== (y = g.firstChild);

                        )
                          (v = g), (g = y);
                        for (;;) {
                          if (g === l) break t;
                          if (
                            (v === s && ++h === c && (p = d),
                            v === f && ++b === u && (m = d),
                            null !== (y = g.nextSibling))
                          )
                            break;
                          v = (g = v).parentNode;
                        }
                        g = y;
                      }
                      s = -1 === p || -1 === m ? null : { start: p, end: m };
                    } else s = null;
                  }
                s = s || { start: 0, end: 0 };
              } else s = null;
              (gn = {
                activeElementDetached: null,
                focusedElem: l,
                selectionRange: s,
              }),
                (Ht = !1),
                (Ll = o);
              do {
                try {
                  ms();
                } catch (e) {
                  if (null === Ll) throw Error(a(330));
                  vs(Ll, e), (Ll = Ll.nextEffect);
                }
              } while (null !== Ll);
              Ll = o;
              do {
                try {
                  for (l = e, s = t; null !== Ll; ) {
                    var w = Ll.effectTag;
                    if ((16 & w && De(Ll.stateNode, ""), 128 & w)) {
                      var x = Ll.alternate;
                      if (null !== x) {
                        var k = x.ref;
                        null !== k &&
                          ("function" == typeof k
                            ? k(null)
                            : (k.current = null));
                      }
                    }
                    switch (1038 & w) {
                      case 2:
                        ul(Ll), (Ll.effectTag &= -3);
                        break;
                      case 6:
                        ul(Ll), (Ll.effectTag &= -3), pl(Ll.alternate, Ll);
                        break;
                      case 1024:
                        Ll.effectTag &= -1025;
                        break;
                      case 1028:
                        (Ll.effectTag &= -1025), pl(Ll.alternate, Ll);
                        break;
                      case 4:
                        pl(Ll.alternate, Ll);
                        break;
                      case 8:
                        dl(l, (c = Ll), s), ll(c);
                    }
                    Ll = Ll.nextEffect;
                  }
                } catch (e) {
                  if (null === Ll) throw Error(a(330));
                  vs(Ll, e), (Ll = Ll.nextEffect);
                }
              } while (null !== Ll);
              if (
                ((k = gn),
                (x = dn()),
                (w = k.focusedElem),
                (s = k.selectionRange),
                x !== w &&
                  w &&
                  w.ownerDocument &&
                  fn(w.ownerDocument.documentElement, w))
              ) {
                null !== s &&
                  pn(w) &&
                  ((x = s.start),
                  void 0 === (k = s.end) && (k = x),
                  "selectionStart" in w
                    ? ((w.selectionStart = x),
                      (w.selectionEnd = Math.min(k, w.value.length)))
                    : (k =
                        ((x = w.ownerDocument || document) && x.defaultView) ||
                        window).getSelection &&
                      ((k = k.getSelection()),
                      (c = w.textContent.length),
                      (l = Math.min(s.start, c)),
                      (s = void 0 === s.end ? l : Math.min(s.end, c)),
                      !k.extend && l > s && ((c = s), (s = l), (l = c)),
                      (c = cn(w, l)),
                      (f = cn(w, s)),
                      c &&
                        f &&
                        (1 !== k.rangeCount ||
                          k.anchorNode !== c.node ||
                          k.anchorOffset !== c.offset ||
                          k.focusNode !== f.node ||
                          k.focusOffset !== f.offset) &&
                        ((x = x.createRange()).setStart(c.node, c.offset),
                        k.removeAllRanges(),
                        l > s
                          ? (k.addRange(x), k.extend(f.node, f.offset))
                          : (x.setEnd(f.node, f.offset), k.addRange(x))))),
                  (x = []);
                for (k = w; (k = k.parentNode); )
                  1 === k.nodeType &&
                    x.push({
                      element: k,
                      left: k.scrollLeft,
                      top: k.scrollTop,
                    });
                for (
                  "function" == typeof w.focus && w.focus(), w = 0;
                  w < x.length;
                  w++
                )
                  ((k = x[w]).element.scrollLeft = k.left),
                    (k.element.scrollTop = k.top);
              }
              (Ht = !!bn), (gn = bn = null), (e.current = n), (Ll = o);
              do {
                try {
                  for (w = e; null !== Ll; ) {
                    var E = Ll.effectTag;
                    if ((36 & E && il(w, Ll.alternate, Ll), 128 & E)) {
                      x = void 0;
                      var _ = Ll.ref;
                      if (null !== _) {
                        var S = Ll.stateNode;
                        Ll.tag,
                          (x = S),
                          "function" == typeof _ ? _(x) : (_.current = x);
                      }
                    }
                    Ll = Ll.nextEffect;
                  }
                } catch (e) {
                  if (null === Ll) throw Error(a(330));
                  vs(Ll, e), (Ll = Ll.nextEffect);
                }
              } while (null !== Ll);
              (Ll = null), Fo(), (Sl = i);
            } else e.current = n;
            if (Ul) (Ul = !1), (Wl = e), (Vl = t);
            else
              for (Ll = o; null !== Ll; )
                (t = Ll.nextEffect), (Ll.nextEffect = null), (Ll = t);
            if (
              (0 === (t = e.firstPendingTime) && (Bl = null),
              1073741823 === t
                ? e === Ql
                  ? ql++
                  : ((ql = 0), (Ql = e))
                : (ql = 0),
              "function" == typeof xs && xs(n.stateNode, r),
              Jl(e),
              zl)
            )
              throw ((zl = !1), (e = Dl), (Dl = null), e);
            return 0 != (8 & Sl) || Qo(), null;
          }
          function ms() {
            for (; null !== Ll; ) {
              var e = Ll.effectTag;
              0 != (256 & e) && nl(Ll.alternate, Ll),
                0 == (512 & e) ||
                  Ul ||
                  ((Ul = !0),
                  Ho(97, function () {
                    return hs(), null;
                  })),
                (Ll = Ll.nextEffect);
            }
          }
          function hs() {
            if (90 !== Vl) {
              var e = 97 < Vl ? 97 : Vl;
              return (Vl = 90), Vo(e, bs);
            }
          }
          function bs() {
            if (null === Wl) return !1;
            var e = Wl;
            if (((Wl = null), 0 != (48 & Sl))) throw Error(a(331));
            var t = Sl;
            for (Sl |= 32, e = e.current.firstEffect; null !== e; ) {
              try {
                var n = e;
                if (0 != (512 & n.effectTag))
                  switch (n.tag) {
                    case 0:
                    case 11:
                    case 15:
                    case 22:
                      rl(5, n), ol(5, n);
                  }
              } catch (t) {
                if (null === e) throw Error(a(330));
                vs(e, t);
              }
              (n = e.nextEffect), (e.nextEffect = null), (e = n);
            }
            return (Sl = t), Qo(), !0;
          }
          function gs(e, t, n) {
            ui(e, (t = bl(e, (t = Za(n, t)), 1073741823))),
              null !== (e = Xl(e, 1073741823)) && Jl(e);
          }
          function vs(e, t) {
            if (3 === e.tag) gs(e, e, t);
            else
              for (var n = e.return; null !== n; ) {
                if (3 === n.tag) {
                  gs(n, e, t);
                  break;
                }
                if (1 === n.tag) {
                  var r = n.stateNode;
                  if (
                    "function" == typeof n.type.getDerivedStateFromError ||
                    ("function" == typeof r.componentDidCatch &&
                      (null === Bl || !Bl.has(r)))
                  ) {
                    ui(n, (e = gl(n, (e = Za(t, e)), 1073741823))),
                      null !== (n = Xl(n, 1073741823)) && Jl(n);
                    break;
                  }
                }
                n = n.return;
              }
          }
          function ys(e, t, n) {
            var r = e.pingCache;
            null !== r && r.delete(t),
              Tl === e && Pl === n
                ? Cl === _l ||
                  (Cl === El && 1073741823 === Nl && Bo() - Il < 500)
                  ? ns(e, Pl)
                  : (Fl = !0)
                : As(e, n) &&
                  ((0 !== (t = e.lastPingedTime) && t < n) ||
                    ((e.lastPingedTime = n), Jl(e)));
          }
          function ws(e, t) {
            var n = e.stateNode;
            null !== n && n.delete(t),
              0 == (t = 0) && (t = $l((t = Gl()), e, null)),
              null !== (e = Xl(e, t)) && Jl(e);
          }
          vl = function (e, t, n) {
            var r = t.expirationTime;
            if (null !== e) {
              var o = t.pendingProps;
              if (e.memoizedProps !== o || po.current) Ma = !0;
              else {
                if (r < n) {
                  switch (((Ma = !1), t.tag)) {
                    case 3:
                      Da(t), Pa();
                      break;
                    case 5:
                      if ((Ri(t), 4 & t.mode && 1 !== n && o.hidden))
                        return (
                          (t.expirationTime = t.childExpirationTime = 1), null
                        );
                      break;
                    case 1:
                      bo(t.type) && wo(t);
                      break;
                    case 4:
                      Ai(t, t.stateNode.containerInfo);
                      break;
                    case 10:
                      (r = t.memoizedProps.value),
                        (o = t.type._context),
                        uo(Yo, o._currentValue),
                        (o._currentValue = r);
                      break;
                    case 13:
                      if (null !== t.memoizedState)
                        return 0 !== (r = t.child.childExpirationTime) && r >= n
                          ? Ha(e, t, n)
                          : (uo(Ii, 1 & Ii.current),
                            null !== (t = Ga(e, t, n)) ? t.sibling : null);
                      uo(Ii, 1 & Ii.current);
                      break;
                    case 19:
                      if (
                        ((r = t.childExpirationTime >= n),
                        0 != (64 & e.effectTag))
                      ) {
                        if (r) return Ka(e, t, n);
                        t.effectTag |= 64;
                      }
                      if (
                        (null !== (o = t.memoizedState) &&
                          ((o.rendering = null), (o.tail = null)),
                        uo(Ii, Ii.current),
                        !r)
                      )
                        return null;
                  }
                  return Ga(e, t, n);
                }
                Ma = !1;
              }
            } else Ma = !1;
            switch (((t.expirationTime = 0), t.tag)) {
              case 2:
                if (
                  ((r = t.type),
                  null !== e &&
                    ((e.alternate = null),
                    (t.alternate = null),
                    (t.effectTag |= 2)),
                  (e = t.pendingProps),
                  (o = ho(t, fo.current)),
                  ri(t, n),
                  (o = Gi(null, t, r, e, o, n)),
                  (t.effectTag |= 1),
                  "object" == typeof o &&
                    null !== o &&
                    "function" == typeof o.render &&
                    void 0 === o.$$typeof)
                ) {
                  if (
                    ((t.tag = 1),
                    (t.memoizedState = null),
                    (t.updateQueue = null),
                    bo(r))
                  ) {
                    var i = !0;
                    wo(t);
                  } else i = !1;
                  (t.memoizedState =
                    null !== o.state && void 0 !== o.state ? o.state : null),
                    ai(t);
                  var l = r.getDerivedStateFromProps;
                  "function" == typeof l && hi(t, r, l, e),
                    (o.updater = bi),
                    (t.stateNode = o),
                    (o._reactInternalFiber = t),
                    wi(t, r, e, n),
                    (t = za(null, t, r, !0, i, n));
                } else (t.tag = 0), Na(null, t, o, n), (t = t.child);
                return t;
              case 16:
                e: {
                  if (
                    ((o = t.elementType),
                    null !== e &&
                      ((e.alternate = null),
                      (t.alternate = null),
                      (t.effectTag |= 2)),
                    (e = t.pendingProps),
                    (function (e) {
                      if (-1 === e._status) {
                        e._status = 0;
                        var t = e._ctor;
                        (t = t()),
                          (e._result = t),
                          t.then(
                            function (t) {
                              0 === e._status &&
                                ((t = t.default),
                                (e._status = 1),
                                (e._result = t));
                            },
                            function (t) {
                              0 === e._status &&
                                ((e._status = 2), (e._result = t));
                            }
                          );
                      }
                    })(o),
                    1 !== o._status)
                  )
                    throw o._result;
                  switch (
                    ((o = o._result),
                    (t.type = o),
                    (i = t.tag = (function (e) {
                      if ("function" == typeof e) return Ss(e) ? 1 : 0;
                      if (null != e) {
                        if ((e = e.$$typeof) === se) return 11;
                        if (e === fe) return 14;
                      }
                      return 2;
                    })(o)),
                    (e = $o(o, e)),
                    i)
                  ) {
                    case 0:
                      t = Ia(null, t, o, e, n);
                      break e;
                    case 1:
                      t = La(null, t, o, e, n);
                      break e;
                    case 11:
                      t = Aa(null, t, o, e, n);
                      break e;
                    case 14:
                      t = ja(null, t, o, $o(o.type, e), r, n);
                      break e;
                  }
                  throw Error(a(306, o, ""));
                }
                return t;
              case 0:
                return (
                  (r = t.type),
                  (o = t.pendingProps),
                  Ia(e, t, r, (o = t.elementType === r ? o : $o(r, o)), n)
                );
              case 1:
                return (
                  (r = t.type),
                  (o = t.pendingProps),
                  La(e, t, r, (o = t.elementType === r ? o : $o(r, o)), n)
                );
              case 3:
                if ((Da(t), (r = t.updateQueue), null === e || null === r))
                  throw Error(a(282));
                if (
                  ((r = t.pendingProps),
                  (o = null !== (o = t.memoizedState) ? o.element : null),
                  li(e, t),
                  fi(t, r, null, n),
                  (r = t.memoizedState.element) === o)
                )
                  Pa(), (t = Ga(e, t, n));
                else {
                  if (
                    ((o = t.stateNode.hydrate) &&
                      ((xa = kn(t.stateNode.containerInfo.firstChild)),
                      (wa = t),
                      (o = ka = !0)),
                    o)
                  )
                    for (n = Ti(t, null, r, n), t.child = n; n; )
                      (n.effectTag = (-3 & n.effectTag) | 1024),
                        (n = n.sibling);
                  else Na(e, t, r, n), Pa();
                  t = t.child;
                }
                return t;
              case 5:
                return (
                  Ri(t),
                  null === e && Sa(t),
                  (r = t.type),
                  (o = t.pendingProps),
                  (i = null !== e ? e.memoizedProps : null),
                  (l = o.children),
                  yn(r, o)
                    ? (l = null)
                    : null !== i && yn(r, i) && (t.effectTag |= 16),
                  Fa(e, t),
                  4 & t.mode && 1 !== n && o.hidden
                    ? ((t.expirationTime = t.childExpirationTime = 1),
                      (t = null))
                    : (Na(e, t, l, n), (t = t.child)),
                  t
                );
              case 6:
                return null === e && Sa(t), null;
              case 13:
                return Ha(e, t, n);
              case 4:
                return (
                  Ai(t, t.stateNode.containerInfo),
                  (r = t.pendingProps),
                  null === e ? (t.child = Si(t, null, r, n)) : Na(e, t, r, n),
                  t.child
                );
              case 11:
                return (
                  (r = t.type),
                  (o = t.pendingProps),
                  Aa(e, t, r, (o = t.elementType === r ? o : $o(r, o)), n)
                );
              case 7:
                return Na(e, t, t.pendingProps, n), t.child;
              case 8:
              case 12:
                return Na(e, t, t.pendingProps.children, n), t.child;
              case 10:
                e: {
                  (r = t.type._context),
                    (o = t.pendingProps),
                    (l = t.memoizedProps),
                    (i = o.value);
                  var s = t.type._context;
                  if (
                    (uo(Yo, s._currentValue), (s._currentValue = i), null !== l)
                  )
                    if (
                      ((s = l.value),
                      0 ==
                        (i = Lr(s, i)
                          ? 0
                          : 0 |
                            ("function" == typeof r._calculateChangedBits
                              ? r._calculateChangedBits(s, i)
                              : 1073741823)))
                    ) {
                      if (l.children === o.children && !po.current) {
                        t = Ga(e, t, n);
                        break e;
                      }
                    } else
                      for (
                        null !== (s = t.child) && (s.return = t);
                        null !== s;

                      ) {
                        var u = s.dependencies;
                        if (null !== u) {
                          l = s.child;
                          for (var c = u.firstContext; null !== c; ) {
                            if (c.context === r && 0 != (c.observedBits & i)) {
                              1 === s.tag &&
                                (((c = si(n, null)).tag = 2), ui(s, c)),
                                s.expirationTime < n && (s.expirationTime = n),
                                null !== (c = s.alternate) &&
                                  c.expirationTime < n &&
                                  (c.expirationTime = n),
                                ni(s.return, n),
                                u.expirationTime < n && (u.expirationTime = n);
                              break;
                            }
                            c = c.next;
                          }
                        } else
                          l =
                            10 === s.tag && s.type === t.type ? null : s.child;
                        if (null !== l) l.return = s;
                        else
                          for (l = s; null !== l; ) {
                            if (l === t) {
                              l = null;
                              break;
                            }
                            if (null !== (s = l.sibling)) {
                              (s.return = l.return), (l = s);
                              break;
                            }
                            l = l.return;
                          }
                        s = l;
                      }
                  Na(e, t, o.children, n), (t = t.child);
                }
                return t;
              case 9:
                return (
                  (o = t.type),
                  (r = (i = t.pendingProps).children),
                  ri(t, n),
                  (r = r((o = oi(o, i.unstable_observedBits)))),
                  (t.effectTag |= 1),
                  Na(e, t, r, n),
                  t.child
                );
              case 14:
                return (
                  (i = $o((o = t.type), t.pendingProps)),
                  ja(e, t, o, (i = $o(o.type, i)), r, n)
                );
              case 15:
                return Ra(e, t, t.type, t.pendingProps, r, n);
              case 17:
                return (
                  (r = t.type),
                  (o = t.pendingProps),
                  (o = t.elementType === r ? o : $o(r, o)),
                  null !== e &&
                    ((e.alternate = null),
                    (t.alternate = null),
                    (t.effectTag |= 2)),
                  (t.tag = 1),
                  bo(r) ? ((e = !0), wo(t)) : (e = !1),
                  ri(t, n),
                  vi(t, r, o),
                  wi(t, r, o, n),
                  za(null, t, r, !0, e, n)
                );
              case 19:
                return Ka(e, t, n);
            }
            throw Error(a(156, t.tag));
          };
          var xs = null,
            ks = null;
          function Es(e, t, n, r) {
            (this.tag = e),
              (this.key = n),
              (this.sibling = this.child = this.return = this.stateNode = this.type = this.elementType = null),
              (this.index = 0),
              (this.ref = null),
              (this.pendingProps = t),
              (this.dependencies = this.memoizedState = this.updateQueue = this.memoizedProps = null),
              (this.mode = r),
              (this.effectTag = 0),
              (this.lastEffect = this.firstEffect = this.nextEffect = null),
              (this.childExpirationTime = this.expirationTime = 0),
              (this.alternate = null);
          }
          function _s(e, t, n, r) {
            return new Es(e, t, n, r);
          }
          function Ss(e) {
            return !(!(e = e.prototype) || !e.isReactComponent);
          }
          function Ts(e, t) {
            var n = e.alternate;
            return (
              null === n
                ? (((n = _s(e.tag, t, e.key, e.mode)).elementType =
                    e.elementType),
                  (n.type = e.type),
                  (n.stateNode = e.stateNode),
                  (n.alternate = e),
                  (e.alternate = n))
                : ((n.pendingProps = t),
                  (n.effectTag = 0),
                  (n.nextEffect = null),
                  (n.firstEffect = null),
                  (n.lastEffect = null)),
              (n.childExpirationTime = e.childExpirationTime),
              (n.expirationTime = e.expirationTime),
              (n.child = e.child),
              (n.memoizedProps = e.memoizedProps),
              (n.memoizedState = e.memoizedState),
              (n.updateQueue = e.updateQueue),
              (t = e.dependencies),
              (n.dependencies =
                null === t
                  ? null
                  : {
                      expirationTime: t.expirationTime,
                      firstContext: t.firstContext,
                      responders: t.responders,
                    }),
              (n.sibling = e.sibling),
              (n.index = e.index),
              (n.ref = e.ref),
              n
            );
          }
          function Os(e, t, n, r, o, i) {
            var l = 2;
            if (((r = e), "function" == typeof e)) Ss(e) && (l = 1);
            else if ("string" == typeof e) l = 5;
            else
              e: switch (e) {
                case ne:
                  return Ps(n.children, o, i, t);
                case le:
                  (l = 8), (o |= 7);
                  break;
                case re:
                  (l = 8), (o |= 1);
                  break;
                case oe:
                  return (
                    ((e = _s(12, n, t, 8 | o)).elementType = oe),
                    (e.type = oe),
                    (e.expirationTime = i),
                    e
                  );
                case ue:
                  return (
                    ((e = _s(13, n, t, o)).type = ue),
                    (e.elementType = ue),
                    (e.expirationTime = i),
                    e
                  );
                case ce:
                  return (
                    ((e = _s(19, n, t, o)).elementType = ce),
                    (e.expirationTime = i),
                    e
                  );
                default:
                  if ("object" == typeof e && null !== e)
                    switch (e.$$typeof) {
                      case ie:
                        l = 10;
                        break e;
                      case ae:
                        l = 9;
                        break e;
                      case se:
                        l = 11;
                        break e;
                      case fe:
                        l = 14;
                        break e;
                      case de:
                        (l = 16), (r = null);
                        break e;
                      case pe:
                        l = 22;
                        break e;
                    }
                  throw Error(a(130, null == e ? e : typeof e, ""));
              }
            return (
              ((t = _s(l, n, t, o)).elementType = e),
              (t.type = r),
              (t.expirationTime = i),
              t
            );
          }
          function Ps(e, t, n, r) {
            return ((e = _s(7, e, r, t)).expirationTime = n), e;
          }
          function Cs(e, t, n) {
            return ((e = _s(6, e, null, t)).expirationTime = n), e;
          }
          function Ms(e, t, n) {
            return (
              ((t = _s(
                4,
                null !== e.children ? e.children : [],
                e.key,
                t
              )).expirationTime = n),
              (t.stateNode = {
                containerInfo: e.containerInfo,
                pendingChildren: null,
                implementation: e.implementation,
              }),
              t
            );
          }
          function Ns(e, t, n) {
            (this.tag = t),
              (this.current = null),
              (this.containerInfo = e),
              (this.pingCache = this.pendingChildren = null),
              (this.finishedExpirationTime = 0),
              (this.finishedWork = null),
              (this.timeoutHandle = -1),
              (this.pendingContext = this.context = null),
              (this.hydrate = n),
              (this.callbackNode = null),
              (this.callbackPriority = 90),
              (this.lastExpiredTime = this.lastPingedTime = this.nextKnownPendingLevel = this.lastSuspendedTime = this.firstSuspendedTime = this.firstPendingTime = 0);
          }
          function As(e, t) {
            var n = e.firstSuspendedTime;
            return (e = e.lastSuspendedTime), 0 !== n && n >= t && e <= t;
          }
          function js(e, t) {
            var n = e.firstSuspendedTime,
              r = e.lastSuspendedTime;
            n < t && (e.firstSuspendedTime = t),
              (r > t || 0 === n) && (e.lastSuspendedTime = t),
              t <= e.lastPingedTime && (e.lastPingedTime = 0),
              t <= e.lastExpiredTime && (e.lastExpiredTime = 0);
          }
          function Rs(e, t) {
            t > e.firstPendingTime && (e.firstPendingTime = t);
            var n = e.firstSuspendedTime;
            0 !== n &&
              (t >= n
                ? (e.firstSuspendedTime = e.lastSuspendedTime = e.nextKnownPendingLevel = 0)
                : t >= e.lastSuspendedTime && (e.lastSuspendedTime = t + 1),
              t > e.nextKnownPendingLevel && (e.nextKnownPendingLevel = t));
          }
          function Fs(e, t) {
            var n = e.lastExpiredTime;
            (0 === n || n > t) && (e.lastExpiredTime = t);
          }
          function Is(e, t, n, r) {
            var o = t.current,
              i = Gl(),
              l = pi.suspense;
            i = $l(i, o, l);
            e: if (n) {
              t: {
                if (Ze((n = n._reactInternalFiber)) !== n || 1 !== n.tag)
                  throw Error(a(170));
                var s = n;
                do {
                  switch (s.tag) {
                    case 3:
                      s = s.stateNode.context;
                      break t;
                    case 1:
                      if (bo(s.type)) {
                        s =
                          s.stateNode.__reactInternalMemoizedMergedChildContext;
                        break t;
                      }
                  }
                  s = s.return;
                } while (null !== s);
                throw Error(a(171));
              }
              if (1 === n.tag) {
                var u = n.type;
                if (bo(u)) {
                  n = yo(n, u, s);
                  break e;
                }
              }
              n = s;
            } else n = co;
            return (
              null === t.context ? (t.context = n) : (t.pendingContext = n),
              ((t = si(i, l)).payload = { element: e }),
              null !== (r = void 0 === r ? null : r) && (t.callback = r),
              ui(o, t),
              Yl(o, i),
              i
            );
          }
          function Ls(e, t) {
            null !== (e = e.memoizedState) &&
              null !== e.dehydrated &&
              e.retryTime < t &&
              (e.retryTime = t);
          }
          function zs(e, t) {
            Ls(e, t), (e = e.alternate) && Ls(e, t);
          }
          function Ds(e, t, n) {
            var r = new Ns(e, t, (n = null != n && !0 === n.hydrate)),
              o = _s(3, null, null, 2 === t ? 7 : 1 === t ? 3 : 0);
            (r.current = o),
              (o.stateNode = r),
              ai(o),
              (e[On] = r.current),
              n &&
                0 !== t &&
                (function (e, t) {
                  var n = Xe(t);
                  _t.forEach(function (e) {
                    dt(e, t, n);
                  }),
                    St.forEach(function (e) {
                      dt(e, t, n);
                    });
                })(0, 9 === e.nodeType ? e : e.ownerDocument),
              (this._internalRoot = r);
          }
          function Bs(e) {
            return !(
              !e ||
              (1 !== e.nodeType &&
                9 !== e.nodeType &&
                11 !== e.nodeType &&
                (8 !== e.nodeType ||
                  " react-mount-point-unstable " !== e.nodeValue))
            );
          }
          function Us(e, t, n) {
            var r =
              3 < arguments.length && void 0 !== arguments[3]
                ? arguments[3]
                : null;
            return {
              $$typeof: te,
              key: null == r ? null : "" + r,
              children: e,
              containerInfo: t,
              implementation: n,
            };
          }
          (Ds.prototype.render = function (e) {
            Is(e, this._internalRoot, null, null);
          }),
            (Ds.prototype.unmount = function () {
              var e = this._internalRoot,
                t = e.containerInfo;
              Is(null, e, null, function () {
                t[On] = null;
              });
            }),
            (pt = function (e) {
              if (13 === e.tag) {
                var t = Go(Gl(), 150, 100);
                Yl(e, t), zs(e, t);
              }
            }),
            (mt = function (e) {
              13 === e.tag && (Yl(e, 3), zs(e, 3));
            }),
            (ht = function (e) {
              if (13 === e.tag) {
                var t = Gl();
                Yl(e, (t = $l(t, e, null))), zs(e, t);
              }
            }),
            (P = function (e, t, n) {
              switch (t) {
                case "input":
                  if (
                    (Se(e, n), (t = n.name), "radio" === n.type && null != t)
                  ) {
                    for (n = e; n.parentNode; ) n = n.parentNode;
                    for (
                      n = n.querySelectorAll(
                        "input[name=" +
                          JSON.stringify("" + t) +
                          '][type="radio"]'
                      ),
                        t = 0;
                      t < n.length;
                      t++
                    ) {
                      var r = n[t];
                      if (r !== e && r.form === e.form) {
                        var o = Nn(r);
                        if (!o) throw Error(a(90));
                        xe(r), Se(r, o);
                      }
                    }
                  }
                  break;
                case "textarea":
                  Ae(e, n);
                  break;
                case "select":
                  null != (t = n.value) && Ce(e, !!n.multiple, t, !1);
              }
            }),
            (R = function (e, t) {
              var n = Sl;
              Sl |= 1;
              try {
                return e(t);
              } finally {
                0 === (Sl = n) && Qo();
              }
            }),
            (F = function (e, t, n, r, o) {
              var i = Sl;
              Sl |= 4;
              try {
                return Vo(98, e.bind(null, t, n, r, o));
              } finally {
                0 === (Sl = i) && Qo();
              }
            }),
            (I = function () {
              0 == (49 & Sl) &&
                ((function () {
                  if (null !== Hl) {
                    var e = Hl;
                    (Hl = null),
                      e.forEach(function (e, t) {
                        Fs(t, e), Jl(t);
                      }),
                      Qo();
                  }
                })(),
                hs());
            }),
            (L = function (e, t) {
              var n = Sl;
              Sl |= 2;
              try {
                return e(t);
              } finally {
                0 === (Sl = n) && Qo();
              }
            });
          !(function (e) {
            var t = e.findFiberByHostInstance;
            !(function (e) {
              if ("undefined" == typeof __REACT_DEVTOOLS_GLOBAL_HOOK__)
                return !1;
              var t = __REACT_DEVTOOLS_GLOBAL_HOOK__;
              if (t.isDisabled || !t.supportsFiber) return !0;
              try {
                var n = t.inject(e);
                (xs = function (e) {
                  try {
                    t.onCommitFiberRoot(
                      n,
                      e,
                      void 0,
                      64 == (64 & e.current.effectTag)
                    );
                  } catch (e) {}
                }),
                  (ks = function (e) {
                    try {
                      t.onCommitFiberUnmount(n, e);
                    } catch (e) {}
                  });
              } catch (e) {}
            })(
              o({}, e, {
                overrideHookState: null,
                overrideProps: null,
                setSuspenseHandler: null,
                scheduleUpdate: null,
                currentDispatcherRef: Y.ReactCurrentDispatcher,
                findHostInstanceByFiber: function (e) {
                  return null ===
                    (e = (function (e) {
                      if (
                        ((e = (function (e) {
                          var t = e.alternate;
                          if (!t) {
                            if (null === (t = Ze(e))) throw Error(a(188));
                            return t !== e ? null : e;
                          }
                          for (var n = e, r = t; ; ) {
                            var o = n.return;
                            if (null === o) break;
                            var i = o.alternate;
                            if (null === i) {
                              if (null !== (r = o.return)) {
                                n = r;
                                continue;
                              }
                              break;
                            }
                            if (o.child === i.child) {
                              for (i = o.child; i; ) {
                                if (i === n) return et(o), e;
                                if (i === r) return et(o), t;
                                i = i.sibling;
                              }
                              throw Error(a(188));
                            }
                            if (n.return !== r.return) (n = o), (r = i);
                            else {
                              for (var l = !1, s = o.child; s; ) {
                                if (s === n) {
                                  (l = !0), (n = o), (r = i);
                                  break;
                                }
                                if (s === r) {
                                  (l = !0), (r = o), (n = i);
                                  break;
                                }
                                s = s.sibling;
                              }
                              if (!l) {
                                for (s = i.child; s; ) {
                                  if (s === n) {
                                    (l = !0), (n = i), (r = o);
                                    break;
                                  }
                                  if (s === r) {
                                    (l = !0), (r = i), (n = o);
                                    break;
                                  }
                                  s = s.sibling;
                                }
                                if (!l) throw Error(a(189));
                              }
                            }
                            if (n.alternate !== r) throw Error(a(190));
                          }
                          if (3 !== n.tag) throw Error(a(188));
                          return n.stateNode.current === n ? e : t;
                        })(e)),
                        !e)
                      )
                        return null;
                      for (var t = e; ; ) {
                        if (5 === t.tag || 6 === t.tag) return t;
                        if (t.child) (t.child.return = t), (t = t.child);
                        else {
                          if (t === e) break;
                          for (; !t.sibling; ) {
                            if (!t.return || t.return === e) return null;
                            t = t.return;
                          }
                          (t.sibling.return = t.return), (t = t.sibling);
                        }
                      }
                      return null;
                    })(e))
                    ? null
                    : e.stateNode;
                },
                findFiberByHostInstance: function (e) {
                  return t ? t(e) : null;
                },
                findHostInstancesForRefresh: null,
                scheduleRefresh: null,
                scheduleRoot: null,
                setRefreshHandler: null,
                getCurrentFiber: null,
              })
            );
          })({
            findFiberByHostInstance: Pn,
            bundleType: 0,
            version: "16.14.0",
            rendererPackageName: "react-dom",
          }),
            (t.createPortal = function (e, t) {
              var n =
                2 < arguments.length && void 0 !== arguments[2]
                  ? arguments[2]
                  : null;
              if (!Bs(t)) throw Error(a(200));
              return Us(e, t, null, n);
            }),
            (t.flushSync = function (e, t) {
              if (0 != (48 & Sl)) throw Error(a(187));
              var n = Sl;
              Sl |= 1;
              try {
                return Vo(99, e.bind(null, t));
              } finally {
                (Sl = n), Qo();
              }
            });
        },
        146: (e, t, n) => {
          "use strict";
          !(function e() {
            if (
              "undefined" != typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ &&
              "function" == typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE
            )
              try {
                __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(e);
              } catch (e) {
                console.error(e);
              }
          })(),
            (e.exports = n(145));
        },
        680: (e) => {
          "use strict";
          var t = [];
          function n(e) {
            for (var n = -1, r = 0; r < t.length; r++)
              if (t[r].identifier === e) {
                n = r;
                break;
              }
            return n;
          }
          function r(e, r) {
            for (var i = {}, a = [], l = 0; l < e.length; l++) {
              var s = e[l],
                u = r.base ? s[0] + r.base : s[0],
                c = i[u] || 0,
                f = "".concat(u, " ").concat(c);
              i[u] = c + 1;
              var d = n(f),
                p = {
                  css: s[1],
                  media: s[2],
                  sourceMap: s[3],
                  supports: s[4],
                  layer: s[5],
                };
              if (-1 !== d) t[d].references++, t[d].updater(p);
              else {
                var m = o(p, r);
                (r.byIndex = l),
                  t.splice(l, 0, { identifier: f, updater: m, references: 1 });
              }
              a.push(f);
            }
            return a;
          }
          function o(e, t) {
            var n = t.domAPI(t);
            return (
              n.update(e),
              function (t) {
                if (t) {
                  if (
                    t.css === e.css &&
                    t.media === e.media &&
                    t.sourceMap === e.sourceMap &&
                    t.supports === e.supports &&
                    t.layer === e.layer
                  )
                    return;
                  n.update((e = t));
                } else n.remove();
              }
            );
          }
          e.exports = function (e, o) {
            var i = r((e = e || []), (o = o || {}));
            return function (e) {
              e = e || [];
              for (var a = 0; a < i.length; a++) {
                var l = n(i[a]);
                t[l].references--;
              }
              for (var s = r(e, o), u = 0; u < i.length; u++) {
                var c = n(i[u]);
                0 === t[c].references && (t[c].updater(), t.splice(c, 1));
              }
              i = s;
            };
          };
        },
        415: (e) => {
          "use strict";
          var t = {};
          e.exports = function (e, n) {
            var r = (function (e) {
              if (void 0 === t[e]) {
                var n = document.querySelector(e);
                if (
                  window.HTMLIFrameElement &&
                  n instanceof window.HTMLIFrameElement
                )
                  try {
                    n = n.contentDocument.head;
                  } catch (e) {
                    n = null;
                  }
                t[e] = n;
              }
              return t[e];
            })(e);
            if (!r)
              throw new Error(
                "Couldn't find a style target. This probably means that the value for the 'insert' parameter is invalid."
              );
            r.appendChild(n);
          };
        },
        352: (e) => {
          "use strict";
          e.exports = function (e) {
            var t = document.createElement("style");
            return e.setAttributes(t, e.attributes), e.insert(t, e.options), t;
          };
        },
        643: (e, t, n) => {
          "use strict";
          e.exports = function (e) {
            var t = n.nc;
            t && e.setAttribute("nonce", t);
          };
        },
        793: (e) => {
          "use strict";
          e.exports = function (e) {
            var t = e.insertStyleElement(e);
            return {
              update: function (n) {
                !(function (e, t, n) {
                  var r = "";
                  n.supports && (r += "@supports (".concat(n.supports, ") {")),
                    n.media && (r += "@media ".concat(n.media, " {"));
                  var o = void 0 !== n.layer;
                  o &&
                    (r += "@layer".concat(
                      n.layer.length > 0 ? " ".concat(n.layer) : "",
                      " {"
                    )),
                    (r += n.css),
                    o && (r += "}"),
                    n.media && (r += "}"),
                    n.supports && (r += "}");
                  var i = n.sourceMap;
                  i &&
                    "undefined" != typeof btoa &&
                    (r += "\n/*# sourceMappingURL=data:application/json;base64,".concat(
                      btoa(unescape(encodeURIComponent(JSON.stringify(i)))),
                      " */"
                    )),
                    t.styleTagTransform(r, e, t.options);
                })(t, e, n);
              },
              remove: function () {
                !(function (e) {
                  if (null === e.parentNode) return !1;
                  e.parentNode.removeChild(e);
                })(t);
              },
            };
          };
        },
        179: (e) => {
          "use strict";
          e.exports = function (e, t) {
            if (t.styleSheet) t.styleSheet.cssText = e;
            else {
              for (; t.firstChild; ) t.removeChild(t.firstChild);
              t.appendChild(document.createTextNode(e));
            }
          };
        },
        518: (e) => {
          "use strict";
          var t = Object.getOwnPropertySymbols,
            n = Object.prototype.hasOwnProperty,
            r = Object.prototype.propertyIsEnumerable;
          function o(e) {
            if (null == e)
              throw new TypeError(
                "Object.assign cannot be called with null or undefined"
              );
            return Object(e);
          }
          e.exports = (function () {
            try {
              if (!Object.assign) return !1;
              var e = new String("abc");
              if (((e[5] = "de"), "5" === Object.getOwnPropertyNames(e)[0]))
                return !1;
              for (var t = {}, n = 0; n < 10; n++)
                t["_" + String.fromCharCode(n)] = n;
              if (
                "0123456789" !==
                Object.getOwnPropertyNames(t)
                  .map(function (e) {
                    return t[e];
                  })
                  .join("")
              )
                return !1;
              var r = {};
              return (
                "abcdefghijklmnopqrst".split("").forEach(function (e) {
                  r[e] = e;
                }),
                "abcdefghijklmnopqrst" ===
                  Object.keys(Object.assign({}, r)).join("")
              );
            } catch (e) {
              return !1;
            }
          })()
            ? Object.assign
            : function (e, i) {
                for (var a, l, s = o(e), u = 1; u < arguments.length; u++) {
                  for (var c in (a = Object(arguments[u])))
                    n.call(a, c) && (s[c] = a[c]);
                  if (t) {
                    l = t(a);
                    for (var f = 0; f < l.length; f++)
                      r.call(a, l[f]) && (s[l[f]] = a[l[f]]);
                  }
                }
                return s;
              };
        },
        173: (e, t, n) => {
          "use strict";
          var r = n(591);
          function o() {}
          function i() {}
          (i.resetWarningCache = o),
            (e.exports = function () {
              function e(e, t, n, o, i, a) {
                if (a !== r) {
                  var l = new Error(
                    "Calling PropTypes validators directly is not supported by the `prop-types` package. Use PropTypes.checkPropTypes() to call them. Read more at http://fb.me/use-check-prop-types"
                  );
                  throw ((l.name = "Invariant Violation"), l);
                }
              }
              function t() {
                return e;
              }
              e.isRequired = e;
              var n = {
                array: e,
                bigint: e,
                bool: e,
                func: e,
                number: e,
                object: e,
                string: e,
                symbol: e,
                any: e,
                arrayOf: t,
                element: e,
                elementType: e,
                instanceOf: t,
                node: e,
                objectOf: t,
                oneOf: t,
                oneOfType: t,
                shape: t,
                exact: t,
                checkPropTypes: i,
                resetWarningCache: o,
              };
              return (n.PropTypes = n), n;
            });
        },
        283: (e, t, n) => {
          e.exports = n(173)();
        },
        591: (e) => {
          "use strict";
          e.exports = "SECRET_DO_NOT_PASS_THIS_OR_YOU_WILL_BE_FIRED";
        },
        250: (e) => {
          var t = "undefined" != typeof Element,
            n = "function" == typeof Map,
            r = "function" == typeof Set,
            o = "function" == typeof ArrayBuffer && !!ArrayBuffer.isView;
          function i(e, a) {
            if (e === a) return !0;
            if (e && a && "object" == typeof e && "object" == typeof a) {
              if (e.constructor !== a.constructor) return !1;
              var l, s, u, c;
              if (Array.isArray(e)) {
                if ((l = e.length) != a.length) return !1;
                for (s = l; 0 != s--; ) if (!i(e[s], a[s])) return !1;
                return !0;
              }
              if (n && e instanceof Map && a instanceof Map) {
                if (e.size !== a.size) return !1;
                for (c = e.entries(); !(s = c.next()).done; )
                  if (!a.has(s.value[0])) return !1;
                for (c = e.entries(); !(s = c.next()).done; )
                  if (!i(s.value[1], a.get(s.value[0]))) return !1;
                return !0;
              }
              if (r && e instanceof Set && a instanceof Set) {
                if (e.size !== a.size) return !1;
                for (c = e.entries(); !(s = c.next()).done; )
                  if (!a.has(s.value[0])) return !1;
                return !0;
              }
              if (o && ArrayBuffer.isView(e) && ArrayBuffer.isView(a)) {
                if ((l = e.length) != a.length) return !1;
                for (s = l; 0 != s--; ) if (e[s] !== a[s]) return !1;
                return !0;
              }
              if (e.constructor === RegExp)
                return e.source === a.source && e.flags === a.flags;
              if (e.valueOf !== Object.prototype.valueOf)
                return e.valueOf() === a.valueOf();
              if (e.toString !== Object.prototype.toString)
                return e.toString() === a.toString();
              if ((l = (u = Object.keys(e)).length) !== Object.keys(a).length)
                return !1;
              for (s = l; 0 != s--; )
                if (!Object.prototype.hasOwnProperty.call(a, u[s])) return !1;
              if (t && e instanceof Element) return !1;
              for (s = l; 0 != s--; )
                if (
                  (("_owner" !== u[s] && "__v" !== u[s] && "__o" !== u[s]) ||
                    !e.$$typeof) &&
                  !i(e[u[s]], a[u[s]])
                )
                  return !1;
              return !0;
            }
            return e != e && a != a;
          }
          e.exports = function (e, t) {
            try {
              return i(e, t);
            } catch (e) {
              if ((e.message || "").match(/stack|recursion/i))
                return (
                  console.warn(
                    "react-fast-compare cannot handle circular refs"
                  ),
                  !1
                );
              throw e;
            }
          };
        },
        138: (e, t) => {
          "use strict";
          var n, r, o, i, a;
          if (
            "undefined" == typeof window ||
            "function" != typeof MessageChannel
          ) {
            var l = null,
              s = null,
              u = function () {
                if (null !== l)
                  try {
                    var e = t.unstable_now();
                    l(!0, e), (l = null);
                  } catch (e) {
                    throw (setTimeout(u, 0), e);
                  }
              },
              c = Date.now();
            (t.unstable_now = function () {
              return Date.now() - c;
            }),
              (n = function (e) {
                null !== l ? setTimeout(n, 0, e) : ((l = e), setTimeout(u, 0));
              }),
              (r = function (e, t) {
                s = setTimeout(e, t);
              }),
              (o = function () {
                clearTimeout(s);
              }),
              (i = function () {
                return !1;
              }),
              (a = t.unstable_forceFrameRate = function () {});
          } else {
            var f = window.performance,
              d = window.Date,
              p = window.setTimeout,
              m = window.clearTimeout;
            if ("undefined" != typeof console) {
              var h = window.cancelAnimationFrame;
              "function" != typeof window.requestAnimationFrame &&
                console.error(
                  "This browser doesn't support requestAnimationFrame. Make sure that you load a polyfill in older browsers. https://fb.me/react-polyfills"
                ),
                "function" != typeof h &&
                  console.error(
                    "This browser doesn't support cancelAnimationFrame. Make sure that you load a polyfill in older browsers. https://fb.me/react-polyfills"
                  );
            }
            if ("object" == typeof f && "function" == typeof f.now)
              t.unstable_now = function () {
                return f.now();
              };
            else {
              var b = d.now();
              t.unstable_now = function () {
                return d.now() - b;
              };
            }
            var g = !1,
              v = null,
              y = -1,
              w = 5,
              x = 0;
            (i = function () {
              return t.unstable_now() >= x;
            }),
              (a = function () {}),
              (t.unstable_forceFrameRate = function (e) {
                0 > e || 125 < e
                  ? console.error(
                      "forceFrameRate takes a positive int between 0 and 125, forcing framerates higher than 125 fps is not unsupported"
                    )
                  : (w = 0 < e ? Math.floor(1e3 / e) : 5);
              });
            var k = new MessageChannel(),
              E = k.port2;
            (k.port1.onmessage = function () {
              if (null !== v) {
                var e = t.unstable_now();
                x = e + w;
                try {
                  v(!0, e) ? E.postMessage(null) : ((g = !1), (v = null));
                } catch (e) {
                  throw (E.postMessage(null), e);
                }
              } else g = !1;
            }),
              (n = function (e) {
                (v = e), g || ((g = !0), E.postMessage(null));
              }),
              (r = function (e, n) {
                y = p(function () {
                  e(t.unstable_now());
                }, n);
              }),
              (o = function () {
                m(y), (y = -1);
              });
          }
          function _(e, t) {
            var n = e.length;
            e.push(t);
            e: for (;;) {
              var r = (n - 1) >>> 1,
                o = e[r];
              if (!(void 0 !== o && 0 < O(o, t))) break e;
              (e[r] = t), (e[n] = o), (n = r);
            }
          }
          function S(e) {
            return void 0 === (e = e[0]) ? null : e;
          }
          function T(e) {
            var t = e[0];
            if (void 0 !== t) {
              var n = e.pop();
              if (n !== t) {
                e[0] = n;
                e: for (var r = 0, o = e.length; r < o; ) {
                  var i = 2 * (r + 1) - 1,
                    a = e[i],
                    l = i + 1,
                    s = e[l];
                  if (void 0 !== a && 0 > O(a, n))
                    void 0 !== s && 0 > O(s, a)
                      ? ((e[r] = s), (e[l] = n), (r = l))
                      : ((e[r] = a), (e[i] = n), (r = i));
                  else {
                    if (!(void 0 !== s && 0 > O(s, n))) break e;
                    (e[r] = s), (e[l] = n), (r = l);
                  }
                }
              }
              return t;
            }
            return null;
          }
          function O(e, t) {
            var n = e.sortIndex - t.sortIndex;
            return 0 !== n ? n : e.id - t.id;
          }
          var P = [],
            C = [],
            M = 1,
            N = null,
            A = 3,
            j = !1,
            R = !1,
            F = !1;
          function I(e) {
            for (var t = S(C); null !== t; ) {
              if (null === t.callback) T(C);
              else {
                if (!(t.startTime <= e)) break;
                T(C), (t.sortIndex = t.expirationTime), _(P, t);
              }
              t = S(C);
            }
          }
          function L(e) {
            if (((F = !1), I(e), !R))
              if (null !== S(P)) (R = !0), n(z);
              else {
                var t = S(C);
                null !== t && r(L, t.startTime - e);
              }
          }
          function z(e, n) {
            (R = !1), F && ((F = !1), o()), (j = !0);
            var a = A;
            try {
              for (
                I(n), N = S(P);
                null !== N && (!(N.expirationTime > n) || (e && !i()));

              ) {
                var l = N.callback;
                if (null !== l) {
                  (N.callback = null), (A = N.priorityLevel);
                  var s = l(N.expirationTime <= n);
                  (n = t.unstable_now()),
                    "function" == typeof s
                      ? (N.callback = s)
                      : N === S(P) && T(P),
                    I(n);
                } else T(P);
                N = S(P);
              }
              if (null !== N) var u = !0;
              else {
                var c = S(C);
                null !== c && r(L, c.startTime - n), (u = !1);
              }
              return u;
            } finally {
              (N = null), (A = a), (j = !1);
            }
          }
          function D(e) {
            switch (e) {
              case 1:
                return -1;
              case 2:
                return 250;
              case 5:
                return 1073741823;
              case 4:
                return 1e4;
              default:
                return 5e3;
            }
          }
          var B = a;
          (t.unstable_IdlePriority = 5),
            (t.unstable_ImmediatePriority = 1),
            (t.unstable_LowPriority = 4),
            (t.unstable_NormalPriority = 3),
            (t.unstable_Profiling = null),
            (t.unstable_UserBlockingPriority = 2),
            (t.unstable_cancelCallback = function (e) {
              e.callback = null;
            }),
            (t.unstable_continueExecution = function () {
              R || j || ((R = !0), n(z));
            }),
            (t.unstable_getCurrentPriorityLevel = function () {
              return A;
            }),
            (t.unstable_getFirstCallbackNode = function () {
              return S(P);
            }),
            (t.unstable_next = function (e) {
              switch (A) {
                case 1:
                case 2:
                case 3:
                  var t = 3;
                  break;
                default:
                  t = A;
              }
              var n = A;
              A = t;
              try {
                return e();
              } finally {
                A = n;
              }
            }),
            (t.unstable_pauseExecution = function () {}),
            (t.unstable_requestPaint = B),
            (t.unstable_runWithPriority = function (e, t) {
              switch (e) {
                case 1:
                case 2:
                case 3:
                case 4:
                case 5:
                  break;
                default:
                  e = 3;
              }
              var n = A;
              A = e;
              try {
                return t();
              } finally {
                A = n;
              }
            }),
            (t.unstable_scheduleCallback = function (e, i, a) {
              var l = t.unstable_now();
              if ("object" == typeof a && null !== a) {
                var s = a.delay;
                (s = "number" == typeof s && 0 < s ? l + s : l),
                  (a = "number" == typeof a.timeout ? a.timeout : D(e));
              } else (a = D(e)), (s = l);
              return (
                (e = {
                  id: M++,
                  callback: i,
                  priorityLevel: e,
                  startTime: s,
                  expirationTime: (a = s + a),
                  sortIndex: -1,
                }),
                s > l
                  ? ((e.sortIndex = s),
                    _(C, e),
                    null === S(P) &&
                      e === S(C) &&
                      (F ? o() : (F = !0), r(L, s - l)))
                  : ((e.sortIndex = a), _(P, e), R || j || ((R = !0), n(z))),
                e
              );
            }),
            (t.unstable_shouldYield = function () {
              var e = t.unstable_now();
              I(e);
              var n = S(P);
              return (
                (n !== N &&
                  null !== N &&
                  null !== n &&
                  null !== n.callback &&
                  n.startTime <= e &&
                  n.expirationTime < N.expirationTime) ||
                i()
              );
            }),
            (t.unstable_wrapCallback = function (e) {
              var t = A;
              return function () {
                var n = A;
                A = t;
                try {
                  return e.apply(this, arguments);
                } finally {
                  A = n;
                }
              };
            });
        },
        965: (e, t, n) => {
          "use strict";
          e.exports = n(138);
        },
        156: (t) => {
          "use strict";
          t.exports = e;
        },
      },
      n = {};
    function r(e) {
      var o = n[e];
      if (void 0 !== o) return o.exports;
      var i = (n[e] = { id: e, loaded: !1, exports: {} });
      return t[e](i, i.exports, r), (i.loaded = !0), i.exports;
    }
    (r.n = (e) => {
      var t = e && e.__esModule ? () => e.default : () => e;
      return r.d(t, { a: t }), t;
    }),
      (r.d = (e, t) => {
        for (var n in t)
          r.o(t, n) &&
            !r.o(e, n) &&
            Object.defineProperty(e, n, { enumerable: !0, get: t[n] });
      }),
      (r.g = (function () {
        if ("object" == typeof globalThis) return globalThis;
        try {
          return this || new Function("return this")();
        } catch (e) {
          if ("object" == typeof window) return window;
        }
      })()),
      (r.o = (e, t) => Object.prototype.hasOwnProperty.call(e, t)),
      (r.r = (e) => {
        "undefined" != typeof Symbol &&
          Symbol.toStringTag &&
          Object.defineProperty(e, Symbol.toStringTag, { value: "Module" }),
          Object.defineProperty(e, "__esModule", { value: !0 });
      }),
      (r.nmd = (e) => ((e.paths = []), e.children || (e.children = []), e)),
      (r.nc = void 0);
    var o = {};
    return (
      (() => {
        "use strict";
        r.r(o), r.d(o, { Feedback: () => At, Tips: () => xt });
        var e = r(156),
          t = r.n(e);
        function n() {
          return (
            (n = Object.assign
              ? Object.assign.bind()
              : function (e) {
                  for (var t = 1; t < arguments.length; t++) {
                    var n = arguments[t];
                    for (var r in n)
                      Object.prototype.hasOwnProperty.call(n, r) &&
                        (e[r] = n[r]);
                  }
                  return e;
                }),
            n.apply(this, arguments)
          );
        }
        var i = r(146);
        function a(e) {
          if (null == e) return window;
          if ("[object Window]" !== e.toString()) {
            var t = e.ownerDocument;
            return (t && t.defaultView) || window;
          }
          return e;
        }
        function l(e) {
          return e instanceof a(e).Element || e instanceof Element;
        }
        function s(e) {
          return e instanceof a(e).HTMLElement || e instanceof HTMLElement;
        }
        function u(e) {
          return (
            "undefined" != typeof ShadowRoot &&
            (e instanceof a(e).ShadowRoot || e instanceof ShadowRoot)
          );
        }
        var c = Math.max,
          f = Math.min,
          d = Math.round;
        function p(e, t) {
          void 0 === t && (t = !1);
          var n = e.getBoundingClientRect(),
            r = 1,
            o = 1;
          if (s(e) && t) {
            var i = e.offsetHeight,
              a = e.offsetWidth;
            a > 0 && (r = d(n.width) / a || 1),
              i > 0 && (o = d(n.height) / i || 1);
          }
          return {
            width: n.width / r,
            height: n.height / o,
            top: n.top / o,
            right: n.right / r,
            bottom: n.bottom / o,
            left: n.left / r,
            x: n.left / r,
            y: n.top / o,
          };
        }
        function m(e) {
          var t = a(e);
          return { scrollLeft: t.pageXOffset, scrollTop: t.pageYOffset };
        }
        function h(e) {
          return e ? (e.nodeName || "").toLowerCase() : null;
        }
        function b(e) {
          return ((l(e) ? e.ownerDocument : e.document) || window.document)
            .documentElement;
        }
        function g(e) {
          return p(b(e)).left + m(e).scrollLeft;
        }
        function v(e) {
          return a(e).getComputedStyle(e);
        }
        function y(e) {
          var t = v(e),
            n = t.overflow,
            r = t.overflowX,
            o = t.overflowY;
          return /auto|scroll|overlay|hidden/.test(n + o + r);
        }
        function w(e, t, n) {
          void 0 === n && (n = !1);
          var r,
            o,
            i = s(t),
            l =
              s(t) &&
              (function (e) {
                var t = e.getBoundingClientRect(),
                  n = d(t.width) / e.offsetWidth || 1,
                  r = d(t.height) / e.offsetHeight || 1;
                return 1 !== n || 1 !== r;
              })(t),
            u = b(t),
            c = p(e, l),
            f = { scrollLeft: 0, scrollTop: 0 },
            v = { x: 0, y: 0 };
          return (
            (i || (!i && !n)) &&
              (("body" !== h(t) || y(u)) &&
                (f =
                  (r = t) !== a(r) && s(r)
                    ? { scrollLeft: (o = r).scrollLeft, scrollTop: o.scrollTop }
                    : m(r)),
              s(t)
                ? (((v = p(t, !0)).x += t.clientLeft), (v.y += t.clientTop))
                : u && (v.x = g(u))),
            {
              x: c.left + f.scrollLeft - v.x,
              y: c.top + f.scrollTop - v.y,
              width: c.width,
              height: c.height,
            }
          );
        }
        function x(e) {
          var t = p(e),
            n = e.offsetWidth,
            r = e.offsetHeight;
          return (
            Math.abs(t.width - n) <= 1 && (n = t.width),
            Math.abs(t.height - r) <= 1 && (r = t.height),
            { x: e.offsetLeft, y: e.offsetTop, width: n, height: r }
          );
        }
        function k(e) {
          return "html" === h(e)
            ? e
            : e.assignedSlot || e.parentNode || (u(e) ? e.host : null) || b(e);
        }
        function E(e) {
          return ["html", "body", "#document"].indexOf(h(e)) >= 0
            ? e.ownerDocument.body
            : s(e) && y(e)
            ? e
            : E(k(e));
        }
        function _(e, t) {
          var n;
          void 0 === t && (t = []);
          var r = E(e),
            o = r === (null == (n = e.ownerDocument) ? void 0 : n.body),
            i = a(r),
            l = o ? [i].concat(i.visualViewport || [], y(r) ? r : []) : r,
            s = t.concat(l);
          return o ? s : s.concat(_(k(l)));
        }
        function S(e) {
          return ["table", "td", "th"].indexOf(h(e)) >= 0;
        }
        function T(e) {
          return s(e) && "fixed" !== v(e).position ? e.offsetParent : null;
        }
        function O(e) {
          for (
            var t = a(e), n = T(e);
            n && S(n) && "static" === v(n).position;

          )
            n = T(n);
          return n &&
            ("html" === h(n) || ("body" === h(n) && "static" === v(n).position))
            ? t
            : n ||
                (function (e) {
                  var t =
                    -1 !== navigator.userAgent.toLowerCase().indexOf("firefox");
                  if (
                    -1 !== navigator.userAgent.indexOf("Trident") &&
                    s(e) &&
                    "fixed" === v(e).position
                  )
                    return null;
                  var n = k(e);
                  for (
                    u(n) && (n = n.host);
                    s(n) && ["html", "body"].indexOf(h(n)) < 0;

                  ) {
                    var r = v(n);
                    if (
                      "none" !== r.transform ||
                      "none" !== r.perspective ||
                      "paint" === r.contain ||
                      -1 !==
                        ["transform", "perspective"].indexOf(r.willChange) ||
                      (t && "filter" === r.willChange) ||
                      (t && r.filter && "none" !== r.filter)
                    )
                      return n;
                    n = n.parentNode;
                  }
                  return null;
                })(e) ||
                t;
        }
        var P = "top",
          C = "bottom",
          M = "right",
          N = "left",
          A = "auto",
          j = [P, C, M, N],
          R = "start",
          F = "end",
          I = "viewport",
          L = "popper",
          z = j.reduce(function (e, t) {
            return e.concat([t + "-" + R, t + "-" + F]);
          }, []),
          D = [].concat(j, [A]).reduce(function (e, t) {
            return e.concat([t, t + "-" + R, t + "-" + F]);
          }, []),
          B = [
            "beforeRead",
            "read",
            "afterRead",
            "beforeMain",
            "main",
            "afterMain",
            "beforeWrite",
            "write",
            "afterWrite",
          ];
        function U(e) {
          var t = new Map(),
            n = new Set(),
            r = [];
          function o(e) {
            n.add(e.name),
              []
                .concat(e.requires || [], e.requiresIfExists || [])
                .forEach(function (e) {
                  if (!n.has(e)) {
                    var r = t.get(e);
                    r && o(r);
                  }
                }),
              r.push(e);
          }
          return (
            e.forEach(function (e) {
              t.set(e.name, e);
            }),
            e.forEach(function (e) {
              n.has(e.name) || o(e);
            }),
            r
          );
        }
        var W = { placement: "bottom", modifiers: [], strategy: "absolute" };
        function V() {
          for (var e = arguments.length, t = new Array(e), n = 0; n < e; n++)
            t[n] = arguments[n];
          return !t.some(function (e) {
            return !(e && "function" == typeof e.getBoundingClientRect);
          });
        }
        function H(e) {
          void 0 === e && (e = {});
          var t = e,
            n = t.defaultModifiers,
            r = void 0 === n ? [] : n,
            o = t.defaultOptions,
            i = void 0 === o ? W : o;
          return function (e, t, n) {
            void 0 === n && (n = i);
            var o,
              a,
              s = {
                placement: "bottom",
                orderedModifiers: [],
                options: Object.assign({}, W, i),
                modifiersData: {},
                elements: { reference: e, popper: t },
                attributes: {},
                styles: {},
              },
              u = [],
              c = !1,
              f = {
                state: s,
                setOptions: function (n) {
                  var o = "function" == typeof n ? n(s.options) : n;
                  d(),
                    (s.options = Object.assign({}, i, s.options, o)),
                    (s.scrollParents = {
                      reference: l(e)
                        ? _(e)
                        : e.contextElement
                        ? _(e.contextElement)
                        : [],
                      popper: _(t),
                    });
                  var a,
                    c,
                    p = (function (e) {
                      var t = U(e);
                      return B.reduce(function (e, n) {
                        return e.concat(
                          t.filter(function (e) {
                            return e.phase === n;
                          })
                        );
                      }, []);
                    })(
                      ((a = [].concat(r, s.options.modifiers)),
                      (c = a.reduce(function (e, t) {
                        var n = e[t.name];
                        return (
                          (e[t.name] = n
                            ? Object.assign({}, n, t, {
                                options: Object.assign(
                                  {},
                                  n.options,
                                  t.options
                                ),
                                data: Object.assign({}, n.data, t.data),
                              })
                            : t),
                          e
                        );
                      }, {})),
                      Object.keys(c).map(function (e) {
                        return c[e];
                      }))
                    );
                  return (
                    (s.orderedModifiers = p.filter(function (e) {
                      return e.enabled;
                    })),
                    s.orderedModifiers.forEach(function (e) {
                      var t = e.name,
                        n = e.options,
                        r = void 0 === n ? {} : n,
                        o = e.effect;
                      if ("function" == typeof o) {
                        var i = o({
                          state: s,
                          name: t,
                          instance: f,
                          options: r,
                        });
                        u.push(i || function () {});
                      }
                    }),
                    f.update()
                  );
                },
                forceUpdate: function () {
                  if (!c) {
                    var e = s.elements,
                      t = e.reference,
                      n = e.popper;
                    if (V(t, n)) {
                      (s.rects = {
                        reference: w(t, O(n), "fixed" === s.options.strategy),
                        popper: x(n),
                      }),
                        (s.reset = !1),
                        (s.placement = s.options.placement),
                        s.orderedModifiers.forEach(function (e) {
                          return (s.modifiersData[e.name] = Object.assign(
                            {},
                            e.data
                          ));
                        });
                      for (var r = 0; r < s.orderedModifiers.length; r++)
                        if (!0 !== s.reset) {
                          var o = s.orderedModifiers[r],
                            i = o.fn,
                            a = o.options,
                            l = void 0 === a ? {} : a,
                            u = o.name;
                          "function" == typeof i &&
                            (s =
                              i({
                                state: s,
                                options: l,
                                name: u,
                                instance: f,
                              }) || s);
                        } else (s.reset = !1), (r = -1);
                    }
                  }
                },
                update:
                  ((o = function () {
                    return new Promise(function (e) {
                      f.forceUpdate(), e(s);
                    });
                  }),
                  function () {
                    return (
                      a ||
                        (a = new Promise(function (e) {
                          Promise.resolve().then(function () {
                            (a = void 0), e(o());
                          });
                        })),
                      a
                    );
                  }),
                destroy: function () {
                  d(), (c = !0);
                },
              };
            if (!V(e, t)) return f;
            function d() {
              u.forEach(function (e) {
                return e();
              }),
                (u = []);
            }
            return (
              f.setOptions(n).then(function (e) {
                !c && n.onFirstUpdate && n.onFirstUpdate(e);
              }),
              f
            );
          };
        }
        var q = { passive: !0 };
        const Q = {
          name: "eventListeners",
          enabled: !0,
          phase: "write",
          fn: function () {},
          effect: function (e) {
            var t = e.state,
              n = e.instance,
              r = e.options,
              o = r.scroll,
              i = void 0 === o || o,
              l = r.resize,
              s = void 0 === l || l,
              u = a(t.elements.popper),
              c = [].concat(t.scrollParents.reference, t.scrollParents.popper);
            return (
              i &&
                c.forEach(function (e) {
                  e.addEventListener("scroll", n.update, q);
                }),
              s && u.addEventListener("resize", n.update, q),
              function () {
                i &&
                  c.forEach(function (e) {
                    e.removeEventListener("scroll", n.update, q);
                  }),
                  s && u.removeEventListener("resize", n.update, q);
              }
            );
          },
          data: {},
        };
        function K(e) {
          return e.split("-")[0];
        }
        function G(e) {
          return e.split("-")[1];
        }
        function $(e) {
          return ["top", "bottom"].indexOf(e) >= 0 ? "x" : "y";
        }
        function Y(e) {
          var t,
            n = e.reference,
            r = e.element,
            o = e.placement,
            i = o ? K(o) : null,
            a = o ? G(o) : null,
            l = n.x + n.width / 2 - r.width / 2,
            s = n.y + n.height / 2 - r.height / 2;
          switch (i) {
            case P:
              t = { x: l, y: n.y - r.height };
              break;
            case C:
              t = { x: l, y: n.y + n.height };
              break;
            case M:
              t = { x: n.x + n.width, y: s };
              break;
            case N:
              t = { x: n.x - r.width, y: s };
              break;
            default:
              t = { x: n.x, y: n.y };
          }
          var u = i ? $(i) : null;
          if (null != u) {
            var c = "y" === u ? "height" : "width";
            switch (a) {
              case R:
                t[u] = t[u] - (n[c] / 2 - r[c] / 2);
                break;
              case F:
                t[u] = t[u] + (n[c] / 2 - r[c] / 2);
            }
          }
          return t;
        }
        var X = { top: "auto", right: "auto", bottom: "auto", left: "auto" };
        function Z(e) {
          var t,
            n = e.popper,
            r = e.popperRect,
            o = e.placement,
            i = e.variation,
            l = e.offsets,
            s = e.position,
            u = e.gpuAcceleration,
            c = e.adaptive,
            f = e.roundOffsets,
            p = e.isFixed,
            m = l.x,
            h = void 0 === m ? 0 : m,
            g = l.y,
            y = void 0 === g ? 0 : g,
            w = "function" == typeof f ? f({ x: h, y }) : { x: h, y };
          (h = w.x), (y = w.y);
          var x = l.hasOwnProperty("x"),
            k = l.hasOwnProperty("y"),
            E = N,
            _ = P,
            S = window;
          if (c) {
            var T = O(n),
              A = "clientHeight",
              j = "clientWidth";
            T === a(n) &&
              "static" !== v((T = b(n))).position &&
              "absolute" === s &&
              ((A = "scrollHeight"), (j = "scrollWidth")),
              (o === P || ((o === N || o === M) && i === F)) &&
                ((_ = C),
                (y -=
                  (p && T === S && S.visualViewport
                    ? S.visualViewport.height
                    : T[A]) - r.height),
                (y *= u ? 1 : -1)),
              (o !== N && ((o !== P && o !== C) || i !== F)) ||
                ((E = M),
                (h -=
                  (p && T === S && S.visualViewport
                    ? S.visualViewport.width
                    : T[j]) - r.width),
                (h *= u ? 1 : -1));
          }
          var R,
            I = Object.assign({ position: s }, c && X),
            L =
              !0 === f
                ? (function (e) {
                    var t = e.x,
                      n = e.y,
                      r = window.devicePixelRatio || 1;
                    return { x: d(t * r) / r || 0, y: d(n * r) / r || 0 };
                  })({ x: h, y })
                : { x: h, y };
          return (
            (h = L.x),
            (y = L.y),
            u
              ? Object.assign(
                  {},
                  I,
                  (((R = {})[_] = k ? "0" : ""),
                  (R[E] = x ? "0" : ""),
                  (R.transform =
                    (S.devicePixelRatio || 1) <= 1
                      ? "translate(" + h + "px, " + y + "px)"
                      : "translate3d(" + h + "px, " + y + "px, 0)"),
                  R)
                )
              : Object.assign(
                  {},
                  I,
                  (((t = {})[_] = k ? y + "px" : ""),
                  (t[E] = x ? h + "px" : ""),
                  (t.transform = ""),
                  t)
                )
          );
        }
        const J = {
            name: "computeStyles",
            enabled: !0,
            phase: "beforeWrite",
            fn: function (e) {
              var t = e.state,
                n = e.options,
                r = n.gpuAcceleration,
                o = void 0 === r || r,
                i = n.adaptive,
                a = void 0 === i || i,
                l = n.roundOffsets,
                s = void 0 === l || l,
                u = {
                  placement: K(t.placement),
                  variation: G(t.placement),
                  popper: t.elements.popper,
                  popperRect: t.rects.popper,
                  gpuAcceleration: o,
                  isFixed: "fixed" === t.options.strategy,
                };
              null != t.modifiersData.popperOffsets &&
                (t.styles.popper = Object.assign(
                  {},
                  t.styles.popper,
                  Z(
                    Object.assign({}, u, {
                      offsets: t.modifiersData.popperOffsets,
                      position: t.options.strategy,
                      adaptive: a,
                      roundOffsets: s,
                    })
                  )
                )),
                null != t.modifiersData.arrow &&
                  (t.styles.arrow = Object.assign(
                    {},
                    t.styles.arrow,
                    Z(
                      Object.assign({}, u, {
                        offsets: t.modifiersData.arrow,
                        position: "absolute",
                        adaptive: !1,
                        roundOffsets: s,
                      })
                    )
                  )),
                (t.attributes.popper = Object.assign({}, t.attributes.popper, {
                  "data-popper-placement": t.placement,
                }));
            },
            data: {},
          },
          ee = {
            name: "offset",
            enabled: !0,
            phase: "main",
            requires: ["popperOffsets"],
            fn: function (e) {
              var t = e.state,
                n = e.options,
                r = e.name,
                o = n.offset,
                i = void 0 === o ? [0, 0] : o,
                a = D.reduce(function (e, n) {
                  return (
                    (e[n] = (function (e, t, n) {
                      var r = K(e),
                        o = [N, P].indexOf(r) >= 0 ? -1 : 1,
                        i =
                          "function" == typeof n
                            ? n(Object.assign({}, t, { placement: e }))
                            : n,
                        a = i[0],
                        l = i[1];
                      return (
                        (a = a || 0),
                        (l = (l || 0) * o),
                        [N, M].indexOf(r) >= 0 ? { x: l, y: a } : { x: a, y: l }
                      );
                    })(n, t.rects, i)),
                    e
                  );
                }, {}),
                l = a[t.placement],
                s = l.x,
                u = l.y;
              null != t.modifiersData.popperOffsets &&
                ((t.modifiersData.popperOffsets.x += s),
                (t.modifiersData.popperOffsets.y += u)),
                (t.modifiersData[r] = a);
            },
          };
        var te = { left: "right", right: "left", bottom: "top", top: "bottom" };
        function ne(e) {
          return e.replace(/left|right|bottom|top/g, function (e) {
            return te[e];
          });
        }
        var re = { start: "end", end: "start" };
        function oe(e) {
          return e.replace(/start|end/g, function (e) {
            return re[e];
          });
        }
        function ie(e, t) {
          var n = t.getRootNode && t.getRootNode();
          if (e.contains(t)) return !0;
          if (n && u(n)) {
            var r = t;
            do {
              if (r && e.isSameNode(r)) return !0;
              r = r.parentNode || r.host;
            } while (r);
          }
          return !1;
        }
        function ae(e) {
          return Object.assign({}, e, {
            left: e.x,
            top: e.y,
            right: e.x + e.width,
            bottom: e.y + e.height,
          });
        }
        function le(e, t) {
          return t === I
            ? ae(
                (function (e) {
                  var t = a(e),
                    n = b(e),
                    r = t.visualViewport,
                    o = n.clientWidth,
                    i = n.clientHeight,
                    l = 0,
                    s = 0;
                  return (
                    r &&
                      ((o = r.width),
                      (i = r.height),
                      /^((?!chrome|android).)*safari/i.test(
                        navigator.userAgent
                      ) || ((l = r.offsetLeft), (s = r.offsetTop))),
                    { width: o, height: i, x: l + g(e), y: s }
                  );
                })(e)
              )
            : l(t)
            ? (function (e) {
                var t = p(e);
                return (
                  (t.top = t.top + e.clientTop),
                  (t.left = t.left + e.clientLeft),
                  (t.bottom = t.top + e.clientHeight),
                  (t.right = t.left + e.clientWidth),
                  (t.width = e.clientWidth),
                  (t.height = e.clientHeight),
                  (t.x = t.left),
                  (t.y = t.top),
                  t
                );
              })(t)
            : ae(
                (function (e) {
                  var t,
                    n = b(e),
                    r = m(e),
                    o = null == (t = e.ownerDocument) ? void 0 : t.body,
                    i = c(
                      n.scrollWidth,
                      n.clientWidth,
                      o ? o.scrollWidth : 0,
                      o ? o.clientWidth : 0
                    ),
                    a = c(
                      n.scrollHeight,
                      n.clientHeight,
                      o ? o.scrollHeight : 0,
                      o ? o.clientHeight : 0
                    ),
                    l = -r.scrollLeft + g(e),
                    s = -r.scrollTop;
                  return (
                    "rtl" === v(o || n).direction &&
                      (l += c(n.clientWidth, o ? o.clientWidth : 0) - i),
                    { width: i, height: a, x: l, y: s }
                  );
                })(b(e))
              );
        }
        function se(e) {
          return Object.assign({}, { top: 0, right: 0, bottom: 0, left: 0 }, e);
        }
        function ue(e, t) {
          return t.reduce(function (t, n) {
            return (t[n] = e), t;
          }, {});
        }
        function ce(e, t) {
          void 0 === t && (t = {});
          var n = t,
            r = n.placement,
            o = void 0 === r ? e.placement : r,
            i = n.boundary,
            a = void 0 === i ? "clippingParents" : i,
            u = n.rootBoundary,
            d = void 0 === u ? I : u,
            m = n.elementContext,
            g = void 0 === m ? L : m,
            y = n.altBoundary,
            w = void 0 !== y && y,
            x = n.padding,
            E = void 0 === x ? 0 : x,
            S = se("number" != typeof E ? E : ue(E, j)),
            T = g === L ? "reference" : L,
            N = e.rects.popper,
            A = e.elements[w ? T : g],
            R = (function (e, t, n) {
              var r =
                  "clippingParents" === t
                    ? (function (e) {
                        var t = _(k(e)),
                          n =
                            ["absolute", "fixed"].indexOf(v(e).position) >= 0 &&
                            s(e)
                              ? O(e)
                              : e;
                        return l(n)
                          ? t.filter(function (e) {
                              return l(e) && ie(e, n) && "body" !== h(e);
                            })
                          : [];
                      })(e)
                    : [].concat(t),
                o = [].concat(r, [n]),
                i = o[0],
                a = o.reduce(function (t, n) {
                  var r = le(e, n);
                  return (
                    (t.top = c(r.top, t.top)),
                    (t.right = f(r.right, t.right)),
                    (t.bottom = f(r.bottom, t.bottom)),
                    (t.left = c(r.left, t.left)),
                    t
                  );
                }, le(e, i));
              return (
                (a.width = a.right - a.left),
                (a.height = a.bottom - a.top),
                (a.x = a.left),
                (a.y = a.top),
                a
              );
            })(l(A) ? A : A.contextElement || b(e.elements.popper), a, d),
            F = p(e.elements.reference),
            z = Y({
              reference: F,
              element: N,
              strategy: "absolute",
              placement: o,
            }),
            D = ae(Object.assign({}, N, z)),
            B = g === L ? D : F,
            U = {
              top: R.top - B.top + S.top,
              bottom: B.bottom - R.bottom + S.bottom,
              left: R.left - B.left + S.left,
              right: B.right - R.right + S.right,
            },
            W = e.modifiersData.offset;
          if (g === L && W) {
            var V = W[o];
            Object.keys(U).forEach(function (e) {
              var t = [M, C].indexOf(e) >= 0 ? 1 : -1,
                n = [P, C].indexOf(e) >= 0 ? "y" : "x";
              U[e] += V[n] * t;
            });
          }
          return U;
        }
        const fe = {
          name: "flip",
          enabled: !0,
          phase: "main",
          fn: function (e) {
            var t = e.state,
              n = e.options,
              r = e.name;
            if (!t.modifiersData[r]._skip) {
              for (
                var o = n.mainAxis,
                  i = void 0 === o || o,
                  a = n.altAxis,
                  l = void 0 === a || a,
                  s = n.fallbackPlacements,
                  u = n.padding,
                  c = n.boundary,
                  f = n.rootBoundary,
                  d = n.altBoundary,
                  p = n.flipVariations,
                  m = void 0 === p || p,
                  h = n.allowedAutoPlacements,
                  b = t.options.placement,
                  g = K(b),
                  v =
                    s ||
                    (g !== b && m
                      ? (function (e) {
                          if (K(e) === A) return [];
                          var t = ne(e);
                          return [oe(e), t, oe(t)];
                        })(b)
                      : [ne(b)]),
                  y = [b].concat(v).reduce(function (e, n) {
                    return e.concat(
                      K(n) === A
                        ? (function (e, t) {
                            void 0 === t && (t = {});
                            var n = t,
                              r = n.placement,
                              o = n.boundary,
                              i = n.rootBoundary,
                              a = n.padding,
                              l = n.flipVariations,
                              s = n.allowedAutoPlacements,
                              u = void 0 === s ? D : s,
                              c = G(r),
                              f = c
                                ? l
                                  ? z
                                  : z.filter(function (e) {
                                      return G(e) === c;
                                    })
                                : j,
                              d = f.filter(function (e) {
                                return u.indexOf(e) >= 0;
                              });
                            0 === d.length && (d = f);
                            var p = d.reduce(function (t, n) {
                              return (
                                (t[n] = ce(e, {
                                  placement: n,
                                  boundary: o,
                                  rootBoundary: i,
                                  padding: a,
                                })[K(n)]),
                                t
                              );
                            }, {});
                            return Object.keys(p).sort(function (e, t) {
                              return p[e] - p[t];
                            });
                          })(t, {
                            placement: n,
                            boundary: c,
                            rootBoundary: f,
                            padding: u,
                            flipVariations: m,
                            allowedAutoPlacements: h,
                          })
                        : n
                    );
                  }, []),
                  w = t.rects.reference,
                  x = t.rects.popper,
                  k = new Map(),
                  E = !0,
                  _ = y[0],
                  S = 0;
                S < y.length;
                S++
              ) {
                var T = y[S],
                  O = K(T),
                  F = G(T) === R,
                  I = [P, C].indexOf(O) >= 0,
                  L = I ? "width" : "height",
                  B = ce(t, {
                    placement: T,
                    boundary: c,
                    rootBoundary: f,
                    altBoundary: d,
                    padding: u,
                  }),
                  U = I ? (F ? M : N) : F ? C : P;
                w[L] > x[L] && (U = ne(U));
                var W = ne(U),
                  V = [];
                if (
                  (i && V.push(B[O] <= 0),
                  l && V.push(B[U] <= 0, B[W] <= 0),
                  V.every(function (e) {
                    return e;
                  }))
                ) {
                  (_ = T), (E = !1);
                  break;
                }
                k.set(T, V);
              }
              if (E)
                for (
                  var H = function (e) {
                      var t = y.find(function (t) {
                        var n = k.get(t);
                        if (n)
                          return n.slice(0, e).every(function (e) {
                            return e;
                          });
                      });
                      if (t) return (_ = t), "break";
                    },
                    q = m ? 3 : 1;
                  q > 0 && "break" !== H(q);
                  q--
                );
              t.placement !== _ &&
                ((t.modifiersData[r]._skip = !0),
                (t.placement = _),
                (t.reset = !0));
            }
          },
          requiresIfExists: ["offset"],
          data: { _skip: !1 },
        };
        function de(e, t, n) {
          return c(e, f(t, n));
        }
        const pe = {
            name: "preventOverflow",
            enabled: !0,
            phase: "main",
            fn: function (e) {
              var t = e.state,
                n = e.options,
                r = e.name,
                o = n.mainAxis,
                i = void 0 === o || o,
                a = n.altAxis,
                l = void 0 !== a && a,
                s = n.boundary,
                u = n.rootBoundary,
                d = n.altBoundary,
                p = n.padding,
                m = n.tether,
                h = void 0 === m || m,
                b = n.tetherOffset,
                g = void 0 === b ? 0 : b,
                v = ce(t, {
                  boundary: s,
                  rootBoundary: u,
                  padding: p,
                  altBoundary: d,
                }),
                y = K(t.placement),
                w = G(t.placement),
                k = !w,
                E = $(y),
                _ = "x" === E ? "y" : "x",
                S = t.modifiersData.popperOffsets,
                T = t.rects.reference,
                A = t.rects.popper,
                j =
                  "function" == typeof g
                    ? g(Object.assign({}, t.rects, { placement: t.placement }))
                    : g,
                F =
                  "number" == typeof j
                    ? { mainAxis: j, altAxis: j }
                    : Object.assign({ mainAxis: 0, altAxis: 0 }, j),
                I = t.modifiersData.offset
                  ? t.modifiersData.offset[t.placement]
                  : null,
                L = { x: 0, y: 0 };
              if (S) {
                if (i) {
                  var z,
                    D = "y" === E ? P : N,
                    B = "y" === E ? C : M,
                    U = "y" === E ? "height" : "width",
                    W = S[E],
                    V = W + v[D],
                    H = W - v[B],
                    q = h ? -A[U] / 2 : 0,
                    Q = w === R ? T[U] : A[U],
                    Y = w === R ? -A[U] : -T[U],
                    X = t.elements.arrow,
                    Z = h && X ? x(X) : { width: 0, height: 0 },
                    J = t.modifiersData["arrow#persistent"]
                      ? t.modifiersData["arrow#persistent"].padding
                      : { top: 0, right: 0, bottom: 0, left: 0 },
                    ee = J[D],
                    te = J[B],
                    ne = de(0, T[U], Z[U]),
                    re = k
                      ? T[U] / 2 - q - ne - ee - F.mainAxis
                      : Q - ne - ee - F.mainAxis,
                    oe = k
                      ? -T[U] / 2 + q + ne + te + F.mainAxis
                      : Y + ne + te + F.mainAxis,
                    ie = t.elements.arrow && O(t.elements.arrow),
                    ae = ie
                      ? "y" === E
                        ? ie.clientTop || 0
                        : ie.clientLeft || 0
                      : 0,
                    le = null != (z = null == I ? void 0 : I[E]) ? z : 0,
                    se = W + oe - le,
                    ue = de(
                      h ? f(V, W + re - le - ae) : V,
                      W,
                      h ? c(H, se) : H
                    );
                  (S[E] = ue), (L[E] = ue - W);
                }
                if (l) {
                  var fe,
                    pe = "x" === E ? P : N,
                    me = "x" === E ? C : M,
                    he = S[_],
                    be = "y" === _ ? "height" : "width",
                    ge = he + v[pe],
                    ve = he - v[me],
                    ye = -1 !== [P, N].indexOf(y),
                    we = null != (fe = null == I ? void 0 : I[_]) ? fe : 0,
                    xe = ye ? ge : he - T[be] - A[be] - we + F.altAxis,
                    ke = ye ? he + T[be] + A[be] - we - F.altAxis : ve,
                    Ee =
                      h && ye
                        ? (function (e, t, n) {
                            var r = de(e, t, n);
                            return r > n ? n : r;
                          })(xe, he, ke)
                        : de(h ? xe : ge, he, h ? ke : ve);
                  (S[_] = Ee), (L[_] = Ee - he);
                }
                t.modifiersData[r] = L;
              }
            },
            requiresIfExists: ["offset"],
          },
          me = {
            name: "arrow",
            enabled: !0,
            phase: "main",
            fn: function (e) {
              var t,
                n = e.state,
                r = e.name,
                o = e.options,
                i = n.elements.arrow,
                a = n.modifiersData.popperOffsets,
                l = K(n.placement),
                s = $(l),
                u = [N, M].indexOf(l) >= 0 ? "height" : "width";
              if (i && a) {
                var c = (function (e, t) {
                    return se(
                      "number" !=
                        typeof (e =
                          "function" == typeof e
                            ? e(
                                Object.assign({}, t.rects, {
                                  placement: t.placement,
                                })
                              )
                            : e)
                        ? e
                        : ue(e, j)
                    );
                  })(o.padding, n),
                  f = x(i),
                  d = "y" === s ? P : N,
                  p = "y" === s ? C : M,
                  m =
                    n.rects.reference[u] +
                    n.rects.reference[s] -
                    a[s] -
                    n.rects.popper[u],
                  h = a[s] - n.rects.reference[s],
                  b = O(i),
                  g = b
                    ? "y" === s
                      ? b.clientHeight || 0
                      : b.clientWidth || 0
                    : 0,
                  v = m / 2 - h / 2,
                  y = c[d],
                  w = g - f[u] - c[p],
                  k = g / 2 - f[u] / 2 + v,
                  E = de(y, k, w),
                  _ = s;
                n.modifiersData[r] =
                  (((t = {})[_] = E), (t.centerOffset = E - k), t);
              }
            },
            effect: function (e) {
              var t = e.state,
                n = e.options.element,
                r = void 0 === n ? "[data-popper-arrow]" : n;
              null != r &&
                ("string" != typeof r ||
                  (r = t.elements.popper.querySelector(r))) &&
                ie(t.elements.popper, r) &&
                (t.elements.arrow = r);
            },
            requires: ["popperOffsets"],
            requiresIfExists: ["preventOverflow"],
          };
        function he(e, t, n) {
          return (
            void 0 === n && (n = { x: 0, y: 0 }),
            {
              top: e.top - t.height - n.y,
              right: e.right - t.width + n.x,
              bottom: e.bottom - t.height + n.y,
              left: e.left - t.width - n.x,
            }
          );
        }
        function be(e) {
          return [P, M, C, N].some(function (t) {
            return e[t] >= 0;
          });
        }
        var ge = H({
            defaultModifiers: [
              Q,
              {
                name: "popperOffsets",
                enabled: !0,
                phase: "read",
                fn: function (e) {
                  var t = e.state,
                    n = e.name;
                  t.modifiersData[n] = Y({
                    reference: t.rects.reference,
                    element: t.rects.popper,
                    strategy: "absolute",
                    placement: t.placement,
                  });
                },
                data: {},
              },
              J,
              {
                name: "applyStyles",
                enabled: !0,
                phase: "write",
                fn: function (e) {
                  var t = e.state;
                  Object.keys(t.elements).forEach(function (e) {
                    var n = t.styles[e] || {},
                      r = t.attributes[e] || {},
                      o = t.elements[e];
                    s(o) &&
                      h(o) &&
                      (Object.assign(o.style, n),
                      Object.keys(r).forEach(function (e) {
                        var t = r[e];
                        !1 === t
                          ? o.removeAttribute(e)
                          : o.setAttribute(e, !0 === t ? "" : t);
                      }));
                  });
                },
                effect: function (e) {
                  var t = e.state,
                    n = {
                      popper: {
                        position: t.options.strategy,
                        left: "0",
                        top: "0",
                        margin: "0",
                      },
                      arrow: { position: "absolute" },
                      reference: {},
                    };
                  return (
                    Object.assign(t.elements.popper.style, n.popper),
                    (t.styles = n),
                    t.elements.arrow &&
                      Object.assign(t.elements.arrow.style, n.arrow),
                    function () {
                      Object.keys(t.elements).forEach(function (e) {
                        var r = t.elements[e],
                          o = t.attributes[e] || {},
                          i = Object.keys(
                            t.styles.hasOwnProperty(e) ? t.styles[e] : n[e]
                          ).reduce(function (e, t) {
                            return (e[t] = ""), e;
                          }, {});
                        s(r) &&
                          h(r) &&
                          (Object.assign(r.style, i),
                          Object.keys(o).forEach(function (e) {
                            r.removeAttribute(e);
                          }));
                      });
                    }
                  );
                },
                requires: ["computeStyles"],
              },
              ee,
              fe,
              pe,
              me,
              {
                name: "hide",
                enabled: !0,
                phase: "main",
                requiresIfExists: ["preventOverflow"],
                fn: function (e) {
                  var t = e.state,
                    n = e.name,
                    r = t.rects.reference,
                    o = t.rects.popper,
                    i = t.modifiersData.preventOverflow,
                    a = ce(t, { elementContext: "reference" }),
                    l = ce(t, { altBoundary: !0 }),
                    s = he(a, r),
                    u = he(l, o, i),
                    c = be(s),
                    f = be(u);
                  (t.modifiersData[n] = {
                    referenceClippingOffsets: s,
                    popperEscapeOffsets: u,
                    isReferenceHidden: c,
                    hasPopperEscaped: f,
                  }),
                    (t.attributes.popper = Object.assign(
                      {},
                      t.attributes.popper,
                      {
                        "data-popper-reference-hidden": c,
                        "data-popper-escaped": f,
                      }
                    ));
                },
              },
            ],
          }),
          ve = r(250),
          ye = r.n(ve),
          we = function (e) {
            return e.reduce(function (e, t) {
              var n = t[0],
                r = t[1];
              return (e[n] = r), e;
            }, {});
          },
          xe =
            "undefined" != typeof window &&
            window.document &&
            window.document.createElement
              ? e.useLayoutEffect
              : e.useEffect,
          ke = [];
        function Ee(t) {
          var n = e.useRef(t);
          return (
            (n.current = t),
            e.useCallback(function () {
              return n.current;
            }, [])
          );
        }
        var _e = function () {};
        function Se(e, t) {
          return (
            void 0 === e && (e = 0),
            void 0 === t && (t = 0),
            function () {
              return {
                width: 0,
                height: 0,
                top: t,
                right: e,
                bottom: t,
                left: e,
                x: 0,
                y: 0,
                toJSON: function () {
                  return null;
                },
              };
            }
          );
        }
        var Te = ["styles", "attributes"],
          Oe = { getBoundingClientRect: Se() },
          Pe = {
            closeOnOutsideClick: !0,
            closeOnTriggerHidden: !1,
            defaultVisible: !1,
            delayHide: 0,
            delayShow: 0,
            followCursor: !1,
            interactive: !1,
            mutationObserverOptions: {
              attributes: !0,
              childList: !0,
              subtree: !0,
            },
            offset: [0, 6],
            trigger: "hover",
          };
        function Ce(t, r) {
          var o, a, l;
          void 0 === t && (t = {}), void 0 === r && (r = {});
          var s = Object.keys(Pe).reduce(function (e, t) {
              var r;
              return n(
                {},
                e,
                (((r = {})[t] = void 0 !== e[t] ? e[t] : Pe[t]), r)
              );
            }, t),
            u = e.useMemo(
              function () {
                return [{ name: "offset", options: { offset: s.offset } }];
              },
              Array.isArray(s.offset) ? s.offset : []
            ),
            c = n({}, r, {
              placement: r.placement || s.placement,
              modifiers: r.modifiers || u,
            }),
            f = e.useState(null),
            d = f[0],
            p = f[1],
            m = e.useState(null),
            h = m[0],
            b = m[1],
            g = (function (t) {
              var n = t.initial,
                r = t.value,
                o = t.onChange,
                i = void 0 === o ? _e : o;
              if (void 0 === n && void 0 === r)
                throw new TypeError(
                  'Either "value" or "initial" variable must be set. Now both are undefined'
                );
              var a = e.useState(n),
                l = a[0],
                s = a[1],
                u = Ee(l),
                c = e.useCallback(
                  function (e) {
                    var t = u(),
                      n = "function" == typeof e ? e(t) : e;
                    "function" == typeof n.persist && n.persist(),
                      s(n),
                      "function" == typeof i && i(n);
                  },
                  [u, i]
                ),
                f = void 0 !== r;
              return [f ? r : l, f ? i : c];
            })({
              initial: s.defaultVisible,
              value: s.visible,
              onChange: s.onVisibleChange,
            }),
            v = g[0],
            y = g[1],
            w = e.useRef();
          e.useEffect(function () {
            return function () {
              return clearTimeout(w.current);
            };
          }, []);
          var x = (function (t, n, r) {
              void 0 === r && (r = {});
              var o = e.useRef(null),
                a = {
                  onFirstUpdate: r.onFirstUpdate,
                  placement: r.placement || "bottom",
                  strategy: r.strategy || "absolute",
                  modifiers: r.modifiers || ke,
                },
                l = e.useState({
                  styles: {
                    popper: { position: a.strategy, left: "0", top: "0" },
                    arrow: { position: "absolute" },
                  },
                  attributes: {},
                }),
                s = l[0],
                u = l[1],
                c = e.useMemo(function () {
                  return {
                    name: "updateState",
                    enabled: !0,
                    phase: "write",
                    fn: function (e) {
                      var t = e.state,
                        n = Object.keys(t.elements);
                      i.flushSync(function () {
                        u({
                          styles: we(
                            n.map(function (e) {
                              return [e, t.styles[e] || {}];
                            })
                          ),
                          attributes: we(
                            n.map(function (e) {
                              return [e, t.attributes[e]];
                            })
                          ),
                        });
                      });
                    },
                    requires: ["computeStyles"],
                  };
                }, []),
                f = e.useMemo(
                  function () {
                    var e = {
                      onFirstUpdate: a.onFirstUpdate,
                      placement: a.placement,
                      strategy: a.strategy,
                      modifiers: [].concat(a.modifiers, [
                        c,
                        { name: "applyStyles", enabled: !1 },
                      ]),
                    };
                    return ye()(o.current, e)
                      ? o.current || e
                      : ((o.current = e), e);
                  },
                  [a.onFirstUpdate, a.placement, a.strategy, a.modifiers, c]
                ),
                d = e.useRef();
              return (
                xe(
                  function () {
                    d.current && d.current.setOptions(f);
                  },
                  [f]
                ),
                xe(
                  function () {
                    if (null != t && null != n) {
                      var e = (r.createPopper || ge)(t, n, f);
                      return (
                        (d.current = e),
                        function () {
                          e.destroy(), (d.current = null);
                        }
                      );
                    }
                  },
                  [t, n, r.createPopper]
                ),
                {
                  state: d.current ? d.current.state : null,
                  styles: s.styles,
                  attributes: s.attributes,
                  update: d.current ? d.current.update : null,
                  forceUpdate: d.current ? d.current.forceUpdate : null,
                }
              );
            })(s.followCursor ? Oe : d, h, c),
            k = x.styles,
            E = x.attributes,
            _ = (function (e, t) {
              if (null == e) return {};
              var n,
                r,
                o = {},
                i = Object.keys(e);
              for (r = 0; r < i.length; r++)
                (n = i[r]), t.indexOf(n) >= 0 || (o[n] = e[n]);
              return o;
            })(x, Te),
            S = _.update,
            T = Ee({
              visible: v,
              triggerRef: d,
              tooltipRef: h,
              finalConfig: s,
            }),
            O = e.useCallback(
              function (e) {
                return Array.isArray(s.trigger)
                  ? s.trigger.includes(e)
                  : s.trigger === e;
              },
              Array.isArray(s.trigger) ? s.trigger : [s.trigger]
            ),
            P = e.useCallback(
              function () {
                clearTimeout(w.current),
                  (w.current = window.setTimeout(function () {
                    return y(!1);
                  }, s.delayHide));
              },
              [s.delayHide, y]
            ),
            C = e.useCallback(
              function () {
                clearTimeout(w.current),
                  (w.current = window.setTimeout(function () {
                    return y(!0);
                  }, s.delayShow));
              },
              [s.delayShow, y]
            ),
            M = e.useCallback(
              function () {
                T().visible ? P() : C();
              },
              [T, P, C]
            );
          e.useEffect(
            function () {
              if (T().finalConfig.closeOnOutsideClick) {
                var e = function (e) {
                  var t,
                    n = T(),
                    r = n.tooltipRef,
                    o = n.triggerRef,
                    i =
                      (null == e.composedPath || null == (t = e.composedPath())
                        ? void 0
                        : t[0]) || e.target;
                  i instanceof Node &&
                    (null == r ||
                      null == o ||
                      r.contains(i) ||
                      o.contains(i) ||
                      P());
                };
                return (
                  document.addEventListener("mousedown", e),
                  function () {
                    return document.removeEventListener("mousedown", e);
                  }
                );
              }
            },
            [T, P]
          ),
            e.useEffect(
              function () {
                if (null != d && O("click"))
                  return (
                    d.addEventListener("click", M),
                    function () {
                      return d.removeEventListener("click", M);
                    }
                  );
              },
              [d, O, M]
            ),
            e.useEffect(
              function () {
                if (null != d && O("double-click"))
                  return (
                    d.addEventListener("dblclick", M),
                    function () {
                      return d.removeEventListener("dblclick", M);
                    }
                  );
              },
              [d, O, M]
            ),
            e.useEffect(
              function () {
                if (null != d && O("right-click")) {
                  var e = function (e) {
                    e.preventDefault(), M();
                  };
                  return (
                    d.addEventListener("contextmenu", e),
                    function () {
                      return d.removeEventListener("contextmenu", e);
                    }
                  );
                }
              },
              [d, O, M]
            ),
            e.useEffect(
              function () {
                if (null != d && O("focus"))
                  return (
                    d.addEventListener("focus", C),
                    d.addEventListener("blur", P),
                    function () {
                      d.removeEventListener("focus", C),
                        d.removeEventListener("blur", P);
                    }
                  );
              },
              [d, O, C, P]
            ),
            e.useEffect(
              function () {
                if (null != d && O("hover"))
                  return (
                    d.addEventListener("mouseenter", C),
                    d.addEventListener("mouseleave", P),
                    function () {
                      d.removeEventListener("mouseenter", C),
                        d.removeEventListener("mouseleave", P);
                    }
                  );
              },
              [d, O, C, P]
            ),
            e.useEffect(
              function () {
                if (null != h && O("hover") && T().finalConfig.interactive)
                  return (
                    h.addEventListener("mouseenter", C),
                    h.addEventListener("mouseleave", P),
                    function () {
                      h.removeEventListener("mouseenter", C),
                        h.removeEventListener("mouseleave", P);
                    }
                  );
              },
              [h, O, C, P, T]
            );
          var N =
            null == _ ||
            null == (o = _.state) ||
            null == (a = o.modifiersData) ||
            null == (l = a.hide)
              ? void 0
              : l.isReferenceHidden;
          return (
            e.useEffect(
              function () {
                s.closeOnTriggerHidden && N && P();
              },
              [s.closeOnTriggerHidden, P, N]
            ),
            e.useEffect(
              function () {
                if (s.followCursor && null != d)
                  return (
                    d.addEventListener("mousemove", e),
                    function () {
                      return d.removeEventListener("mousemove", e);
                    }
                  );
                function e(e) {
                  var t = e.clientX,
                    n = e.clientY;
                  (Oe.getBoundingClientRect = Se(t, n)), null == S || S();
                }
              },
              [s.followCursor, d, S]
            ),
            e.useEffect(
              function () {
                if (
                  null != h &&
                  null != S &&
                  null != s.mutationObserverOptions
                ) {
                  var e = new MutationObserver(S);
                  return (
                    e.observe(h, s.mutationObserverOptions),
                    function () {
                      return e.disconnect();
                    }
                  );
                }
              },
              [s.mutationObserverOptions, h, S]
            ),
            n(
              {
                getArrowProps: function (e) {
                  return (
                    void 0 === e && (e = {}),
                    n({}, e, E.arrow, {
                      style: n({}, e.style, k.arrow),
                      "data-popper-arrow": !0,
                    })
                  );
                },
                getTooltipProps: function (e) {
                  return (
                    void 0 === e && (e = {}),
                    n({}, e, { style: n({}, e.style, k.popper) }, E.popper, {
                      "data-popper-interactive": s.interactive,
                    })
                  );
                },
                setTooltipRef: b,
                setTriggerRef: p,
                tooltipRef: h,
                triggerRef: d,
                visible: v,
              },
              _
            )
          );
        }
        var Me = r(659),
          Ne = r(283),
          Ae = r.n(Ne),
          je =
            "undefined" != typeof globalThis
              ? globalThis
              : "undefined" != typeof window
              ? window
              : void 0 !== r.g
              ? r.g
              : "undefined" != typeof self
              ? self
              : {};
        function Re(e, t) {
          return e((t = { exports: {} }), t.exports), t.exports;
        }
        var Fe = Re(function (e) {
            !(function (t) {
              var n = function (e, t, r) {
                  if (!s(t) || c(t) || f(t) || d(t) || l(t)) return t;
                  var o,
                    i = 0,
                    a = 0;
                  if (u(t))
                    for (o = [], a = t.length; i < a; i++)
                      o.push(n(e, t[i], r));
                  else
                    for (var p in ((o = {}), t))
                      Object.prototype.hasOwnProperty.call(t, p) &&
                        (o[e(p, r)] = n(e, t[p], r));
                  return o;
                },
                r = function (e) {
                  return p(e)
                    ? e
                    : (e = e.replace(/[\-_\s]+(.)?/g, function (e, t) {
                        return t ? t.toUpperCase() : "";
                      }))
                        .substr(0, 1)
                        .toLowerCase() + e.substr(1);
                },
                o = function (e) {
                  var t = r(e);
                  return t.substr(0, 1).toUpperCase() + t.substr(1);
                },
                i = function (e, t) {
                  return (function (e, t) {
                    var n = (t = t || {}).separator || "_",
                      r = t.split || /(?=[A-Z])/;
                    return e.split(r).join(n);
                  })(e, t).toLowerCase();
                },
                a = Object.prototype.toString,
                l = function (e) {
                  return "function" == typeof e;
                },
                s = function (e) {
                  return e === Object(e);
                },
                u = function (e) {
                  return "[object Array]" == a.call(e);
                },
                c = function (e) {
                  return "[object Date]" == a.call(e);
                },
                f = function (e) {
                  return "[object RegExp]" == a.call(e);
                },
                d = function (e) {
                  return "[object Boolean]" == a.call(e);
                },
                p = function (e) {
                  return (e -= 0) == e;
                },
                m = function (e, t) {
                  var n = t && "process" in t ? t.process : t;
                  return "function" != typeof n
                    ? e
                    : function (t, r) {
                        return n(t, e, r);
                      };
                },
                h = {
                  camelize: r,
                  decamelize: i,
                  pascalize: o,
                  depascalize: i,
                  camelizeKeys: function (e, t) {
                    return n(m(r, t), e);
                  },
                  decamelizeKeys: function (e, t) {
                    return n(m(i, t), e, t);
                  },
                  pascalizeKeys: function (e, t) {
                    return n(m(o, t), e);
                  },
                  depascalizeKeys: function () {
                    return this.decamelizeKeys.apply(this, arguments);
                  },
                };
              e.exports ? (e.exports = h) : (t.humps = h);
            })(je);
          }).decamelize,
          Ie = Re(function (e) {
            function t() {
              return (
                (e.exports = t =
                  Object.assign ||
                  function (e) {
                    for (var t = 1; t < arguments.length; t++) {
                      var n = arguments[t];
                      for (var r in n)
                        Object.prototype.hasOwnProperty.call(n, r) &&
                          (e[r] = n[r]);
                    }
                    return e;
                  }),
                t.apply(this, arguments)
              );
            }
            e.exports = t;
          }),
          Le = function (e, t) {
            (null == t || t > e.length) && (t = e.length);
            for (var n = 0, r = new Array(t); n < t; n++) r[n] = e[n];
            return r;
          },
          ze = function (e, t) {
            return (
              (function (e) {
                if (Array.isArray(e)) return e;
              })(e) ||
              (function (e, t) {
                if (
                  "undefined" != typeof Symbol &&
                  Symbol.iterator in Object(e)
                ) {
                  var n = [],
                    r = !0,
                    o = !1,
                    i = void 0;
                  try {
                    for (
                      var a, l = e[Symbol.iterator]();
                      !(r = (a = l.next()).done) &&
                      (n.push(a.value), !t || n.length !== t);
                      r = !0
                    );
                  } catch (e) {
                    (o = !0), (i = e);
                  } finally {
                    try {
                      r || null == l.return || l.return();
                    } finally {
                      if (o) throw i;
                    }
                  }
                  return n;
                }
              })(e, t) ||
              (function (e, t) {
                if (e) {
                  if ("string" == typeof e) return Le(e, t);
                  var n = Object.prototype.toString.call(e).slice(8, -1);
                  return (
                    "Object" === n && e.constructor && (n = e.constructor.name),
                    "Map" === n || "Set" === n
                      ? Array.from(e)
                      : "Arguments" === n ||
                        /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)
                      ? Le(e, t)
                      : void 0
                  );
                }
              })(e, t) ||
              (function () {
                throw new TypeError(
                  "Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."
                );
              })()
            );
          },
          De = (0, e.createContext)(null);
        function Be(e) {
          var t = e.root,
            n = e.children;
          return (0, i.createPortal)(n, t);
        }
        function Ue(n) {
          var r = (0, e.forwardRef)(function (r, o) {
            var i,
              a,
              l = r.mode,
              s = r.delegatesFocus,
              u = r.styleSheets,
              c = r.ssr,
              f = r.children,
              d = (function (e, t) {
                if (null == e) return {};
                var n,
                  r,
                  o = (function (e, t) {
                    if (null == e) return {};
                    var n,
                      r,
                      o = {},
                      i = Object.keys(e);
                    for (r = 0; r < i.length; r++)
                      (n = i[r]), t.indexOf(n) >= 0 || (o[n] = e[n]);
                    return o;
                  })(e, t);
                if (Object.getOwnPropertySymbols) {
                  var i = Object.getOwnPropertySymbols(e);
                  for (r = 0; r < i.length; r++)
                    (n = i[r]),
                      t.indexOf(n) >= 0 ||
                        (Object.prototype.propertyIsEnumerable.call(e, n) &&
                          (o[n] = e[n]));
                }
                return o;
              })(r, [
                "mode",
                "delegatesFocus",
                "styleSheets",
                "ssr",
                "children",
              ]),
              p =
                ((a = (0, e.useRef)((i = o) && i.current)),
                (0, e.useEffect)(
                  function () {
                    i && (i.current = a.current);
                  },
                  [i]
                ),
                a),
              m = (0, e.useState)(null),
              h = ze(m, 2),
              b = h[0],
              g = h[1],
              v = "node_".concat(l).concat(s);
            return (
              (0, e.useEffect)(
                function () {
                  if (p.current)
                    try {
                      if (("function" == typeof o && o(p.current), c)) {
                        var e = p.current.shadowRoot;
                        return void g(e);
                      }
                      var t = p.current.attachShadow({
                        mode: l,
                        delegatesFocus: s,
                      });
                      u.length > 0 && (t.adoptedStyleSheets = u), g(t);
                    } catch (e) {
                      !(function (e) {
                        var t = e.error,
                          n = e.styleSheets,
                          r = e.root;
                        if ("NotSupportedError" !== t.name) throw t;
                        n.length > 0 && (r.adoptedStyleSheets = n);
                      })({ error: e, styleSheets: u, root: b });
                    }
                },
                [o, p, u]
              ),
              t().createElement(
                t().Fragment,
                null,
                t().createElement(
                  n.tag,
                  Ie({ key: v, ref: p }, d),
                  (b || c) &&
                    t().createElement(
                      De.Provider,
                      { value: b },
                      c
                        ? t().createElement(
                            "template",
                            { shadowroot: "open" },
                            n.render({ root: b, ssr: c, children: f })
                          )
                        : t().createElement(
                            Be,
                            { root: b },
                            n.render({ root: b, ssr: c, children: f })
                          )
                    )
                )
              )
            );
          });
          return (
            (r.propTypes = {
              mode: Ae().oneOf(["open", "closed"]),
              delegatesFocus: Ae().bool,
              styleSheets: Ae().arrayOf(
                Ae().instanceOf(globalThis.CSSStyleSheet)
              ),
              ssr: Ae().bool,
              children: Ae().node,
            }),
            (r.defaultProps = {
              mode: "open",
              delegatesFocus: !1,
              styleSheets: [],
              ssr: !1,
              children: null,
            }),
            r
          );
        }
        (Be.propTypes = { root: Ae().object.isRequired, children: Ae().node }),
          (Be.defaultProps = { children: null });
        var We = new Map();
        const Ve = (function () {
          var e =
              arguments.length > 0 && void 0 !== arguments[0]
                ? arguments[0]
                : {},
            t =
              arguments.length > 1 && void 0 !== arguments[1]
                ? arguments[1]
                : "core",
            n =
              arguments.length > 2 && void 0 !== arguments[2]
                ? arguments[2]
                : function (e) {
                    return e.children;
                  };
          return new Proxy(e, {
            get: function (e, r) {
              var o = Fe(r, { separator: "-" }),
                i = "".concat(t, "-").concat(o);
              return (
                We.has(i) || We.set(i, Ue({ tag: o, render: n })), We.get(i)
              );
            },
          });
        })();
        var He = r(680),
          qe = r.n(He),
          Qe = r(793),
          Ke = r.n(Qe),
          Ge = r(415),
          $e = r.n(Ge),
          Ye = r(643),
          Xe = r.n(Ye),
          Ze = r(352),
          Je = r.n(Ze),
          et = r(179),
          tt = r.n(et),
          nt = r(191),
          rt = {};
        (rt.styleTagTransform = tt()),
          (rt.setAttributes = Xe()),
          (rt.insert = $e().bind(null, "head")),
          (rt.domAPI = Ke()),
          (rt.insertStyleElement = Je()),
          qe()(nt.Z, rt),
          nt.Z && nt.Z.locals && nt.Z.locals;
        const ot = function (e) {
          var n = e.margin;
          return t().createElement(
            "svg",
            {
              width: "19",
              height: "19",
              strokeWidth: "2",
              viewBox: "0 0 24 24",
              fill: "none",
              xmlns: "http://www.w3.org/2000/svg",
              style: { margin: n },
            },
            t().createElement("path", {
              d: "M12 11.5V16.5",
              stroke: "currentColor",
              strokeLinecap: "round",
              strokeLinejoin: "round",
            }),
            t().createElement("path", {
              d: "M12 7.51L12.01 7.49889",
              stroke: "currentColor",
              strokeLinecap: "round",
              strokeLinejoin: "round",
            }),
            t().createElement("path", {
              d:
                "M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z",
              stroke: "currentColor",
              strokeLinecap: "round",
              strokeLinejoin: "round",
            })
          );
        };
        var it = 5e3;
        function at(e, t, n, r, o) {
          r();
          var i = !1;
          e.target.id.includes("mephisto-worker-addons-tips__header-input") &&
            (i = !0);
          var a = i ? e.target.value.length : t.header.length,
            l = i ? t.text.length : e.target.value.length;
          a > o.header
            ? n({ type: "header-too-long" })
            : l > o.body
            ? n({ type: "body-too-long" })
            : a <= o.header && l <= o.body && n({ type: "return-to-default" });
        }
        function lt(e, t, n, r) {
          return e
            ? null !== r.errorIndexes || n.includes("")
            : t.length <= 0 || 1 === r.status || 4 === r.status;
        }
        function st(e, t) {
          var n = Object.keys(e);
          if (Object.getOwnPropertySymbols) {
            var r = Object.getOwnPropertySymbols(e);
            t &&
              (r = r.filter(function (t) {
                return Object.getOwnPropertyDescriptor(e, t).enumerable;
              })),
              n.push.apply(n, r);
          }
          return n;
        }
        function ut(e) {
          for (var t = 1; t < arguments.length; t++) {
            var n = null != arguments[t] ? arguments[t] : {};
            t % 2
              ? st(Object(n), !0).forEach(function (t) {
                  ct(e, t, n[t]);
                })
              : Object.getOwnPropertyDescriptors
              ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n))
              : st(Object(n)).forEach(function (t) {
                  Object.defineProperty(
                    e,
                    t,
                    Object.getOwnPropertyDescriptor(n, t)
                  );
                });
          }
          return e;
        }
        function ct(e, t, n) {
          return (
            t in e
              ? Object.defineProperty(e, t, {
                  value: n,
                  enumerable: !0,
                  configurable: !0,
                  writable: !0,
                })
              : (e[t] = n),
            e
          );
        }
        function ft(e, t) {
          var n = ut({}, e);
          switch (t.type) {
            case "return-to-default":
              return (n.status = 0), (n.text = ""), n;
            case "loading":
              return (n.status = 1), (n.text = "Loading"), n;
            case "success":
              return (
                (n.status = 2),
                (n.text = "✅ Your tip has been submitted for review"),
                n
              );
            case "error":
              return (
                (n.status = 3),
                (n.text = "❌ Something went wrong when submitting your tip"),
                n
              );
            case "header-too-long":
              return (
                (n.status = 4), (n.text = "📝 Your tip header is too long"), n
              );
            case "body-too-long":
              return (
                (n.status = 5), (n.text = "📝 Your tip body is too long"), n
              );
            default:
              throw new Error();
          }
        }
        function dt(e, t) {
          var n = ut({}, e);
          switch (t.type) {
            case "return-to-default":
              return (n.status = 0), (n.text = ""), (n.errorIndexes = null), n;
            case "loading":
              return (
                (n.status = 1), (n.text = "Loading"), (n.errorIndexes = null), n
              );
            case "success":
              return (
                (n.status = 2),
                (n.text = "✅ Your feedback has been submitted for review"),
                (n.errorIndexes = null),
                n
              );
            case "error":
              return (
                (n.status = 3),
                (n.text =
                  "❌ Something went wrong when submitting your feedback"),
                (n.errorIndexes = null),
                n
              );
            case "too-long":
              return (
                (n.status = 4),
                (n.text = "📝 Your feedback message is too long"),
                (n.errorIndexes = null),
                n
              );
            case "multiple-errors":
              return (
                (n.status = 5),
                (n.errorIndexes = t.errorIndexes),
                (n.text =
                  "📝 Your feedback message for this question is too long"),
                n
              );
            default:
              throw new Error();
          }
        }
        function pt(e, t) {
          return (
            (function (e) {
              if (Array.isArray(e)) return e;
            })(e) ||
            (function (e, t) {
              var n =
                null == e
                  ? null
                  : ("undefined" != typeof Symbol && e[Symbol.iterator]) ||
                    e["@@iterator"];
              if (null != n) {
                var r,
                  o,
                  i = [],
                  a = !0,
                  l = !1;
                try {
                  for (
                    n = n.call(e);
                    !(a = (r = n.next()).done) &&
                    (i.push(r.value), !t || i.length !== t);
                    a = !0
                  );
                } catch (e) {
                  (l = !0), (o = e);
                } finally {
                  try {
                    a || null == n.return || n.return();
                  } finally {
                    if (l) throw o;
                  }
                }
                return i;
              }
            })(e, t) ||
            (function (e, t) {
              if (e) {
                if ("string" == typeof e) return mt(e, t);
                var n = Object.prototype.toString.call(e).slice(8, -1);
                return (
                  "Object" === n && e.constructor && (n = e.constructor.name),
                  "Map" === n || "Set" === n
                    ? Array.from(e)
                    : "Arguments" === n ||
                      /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)
                    ? mt(e, t)
                    : void 0
                );
              }
            })(e, t) ||
            (function () {
              throw new TypeError(
                "Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."
              );
            })()
          );
        }
        function mt(e, t) {
          (null == t || t > e.length) && (t = e.length);
          for (var n = 0, r = new Array(t); n < t; n++) r[n] = e[n];
          return r;
        }
        const ht = function (n) {
            var r = n.stylePrefixWithNoHeadlessPrefix,
              o = n.stylePrefix,
              i = n.handleSubmit,
              a = n.maxLengths,
              l = pt((0, e.useState)({ header: "", text: "" }), 2),
              s = l[0],
              u = l[1],
              c = (0, Me.useMephistoTask)().handleMetadataSubmit,
              f = pt((0, e.useReducer)(ft, { status: 0, text: "" }), 2),
              d = f[0],
              p = f[1];
            return t().createElement(
              e.Fragment,
              null,
              t().createElement(
                "h1",
                { className: "".concat(o, "header1") },
                "Submit A Tip: "
              ),
              t().createElement(
                "label",
                {
                  htmlFor: "".concat(o, "header-input"),
                  className: "".concat(o, "label"),
                },
                "Tip Headline:"
              ),
              t().createElement("input", {
                id: "".concat(o, "header-input"),
                className: 4 == d.status ? "".concat(o, "input-error") : void 0,
                placeholder: "Write your tip's headline here...",
                value: s.header,
                onChange: function (e) {
                  return at(
                    e,
                    s,
                    p,
                    function () {
                      return u({ header: e.target.value, text: s.text });
                    },
                    a
                  );
                },
                disabled: 1 === d.status,
              }),
              t().createElement(
                "label",
                {
                  htmlFor: "".concat(o, "text-input"),
                  className: "".concat(o, "label"),
                },
                "Tip Body:"
              ),
              t().createElement("textarea", {
                placeholder: "Write your tip body here...",
                id: "".concat(o, "text-input"),
                className: 5 == d.status ? "".concat(o, "input-error") : void 0,
                value: s.text,
                onChange: function (e) {
                  return at(
                    e,
                    s,
                    p,
                    function () {
                      return u({ header: s.header, text: e.target.value });
                    },
                    a
                  );
                },
                disabled: 1 === d.status,
              }),
              (2 === d.status ||
                3 === d.status ||
                4 === d.status ||
                5 === d.status) &&
                t().createElement(
                  "div",
                  {
                    className: ""
                      .concat(r)
                      .concat(2 === d.status ? "green" : "red", "-box"),
                  },
                  d.text
                ),
              t().createElement(
                "button",
                {
                  disabled:
                    1 === d.status ||
                    4 === d.status ||
                    5 === d.status ||
                    0 === s.text.length ||
                    0 === s.header.length,
                  className: "".concat(o, "button"),
                  onClick: function () {
                    return (function (e, t, n, r, o) {
                      e
                        ? e(r)
                        : (n({ type: "loading" }),
                          t(
                            (function (e, t) {
                              if (!e || "string" != typeof e)
                                throw new Error("Tip header is not a string");
                              if (!t || "string" != typeof t)
                                throw new Error("Tip text is not a string");
                              return { header: e, text: t, type: "tips" };
                            })(r.header, r.text)
                          )
                            .then(function (e) {
                              "Submitted metadata" === e.status &&
                                (o({ header: "", text: "" }),
                                n({ type: "success" }),
                                setTimeout(function () {
                                  n({ type: "return-to-default" });
                                }, it));
                            })
                            .catch(function (e) {
                              console.error(e),
                                n({ type: "error" }),
                                setTimeout(function () {
                                  n({ type: "return-to-default" });
                                }, it);
                            }));
                    })(i, c, p, s, u);
                  },
                },
                1 === d.status
                  ? t().createElement("span", {
                      className: "".concat(r, "loader"),
                    })
                  : "Submit Tip"
              )
            );
          },
          bt = function (e) {
            var n = e.tipsArr,
              r = e.stylePrefix,
              o = e.maxPopupHeight,
              i = n.map(function (e, n) {
                return t().createElement(
                  "li",
                  { key: "tip-".concat(n + 1), className: "".concat(r, "tip") },
                  t().createElement(
                    "h2",
                    { className: "".concat(r, "header2") },
                    e.header
                  ),
                  t().createElement(
                    "p",
                    { className: "".concat(r, "text") },
                    e.text
                  )
                );
              });
            return t().createElement(
              "ul",
              {
                style: { maxHeight: "calc(".concat(o, "/2)") },
                className: "".concat(r, "list"),
              },
              n.length > 0
                ? i
                : t().createElement(
                    "h2",
                    {
                      className: ""
                        .concat(r, "header2  ")
                        .concat(r, "no-submissions"),
                    },
                    "There are no submitted tips!"
                  )
            );
          },
          gt = function () {
            return t().createElement(
              "svg",
              {
                width: "24",
                height: "24",
                strokeWidth: "1.5",
                viewBox: "0 0 24 24",
                fill: "none",
                xmlns: "http://www.w3.org/2000/svg",
              },
              t().createElement("path", {
                d:
                  "M9.17218 14.8284L12.0006 12M14.829 9.17157L12.0006 12M12.0006 12L9.17218 9.17157M12.0006 12L14.829 14.8284",
                stroke: "currentColor",
                strokeLinecap: "round",
                strokeLinejoin: "round",
              }),
              t().createElement("path", {
                d:
                  "M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z",
                stroke: "currentColor",
                strokeLinecap: "round",
                strokeLinejoin: "round",
              })
            );
          };
        function vt() {
          return (
            (vt = Object.assign
              ? Object.assign.bind()
              : function (e) {
                  for (var t = 1; t < arguments.length; t++) {
                    var n = arguments[t];
                    for (var r in n)
                      Object.prototype.hasOwnProperty.call(n, r) &&
                        (e[r] = n[r]);
                  }
                  return e;
                }),
            vt.apply(this, arguments)
          );
        }
        function yt(e, t) {
          (null == t || t > e.length) && (t = e.length);
          for (var n = 0, r = new Array(t); n < t; n++) r[n] = e[n];
          return r;
        }
        function wt(e) {
          var n = e.headless,
            r = e.children;
          return n
            ? t().createElement("div", null, r)
            : t().createElement(Ve.div, null, r);
        }
        const xt = function (n) {
          var r,
            o,
            i = n.list,
            a = n.handleSubmit,
            l = n.disableUserSubmission,
            s = n.headless,
            u = n.maxHeight,
            c = n.width,
            f = n.placement,
            d = n.maxHeaderLength,
            p = n.maxTextLength,
            m =
              ((r = (0, e.useState)(!1)),
              (o = 2),
              (function (e) {
                if (Array.isArray(e)) return e;
              })(r) ||
                (function (e, t) {
                  var n =
                    null == e
                      ? null
                      : ("undefined" != typeof Symbol && e[Symbol.iterator]) ||
                        e["@@iterator"];
                  if (null != n) {
                    var r,
                      o,
                      i = [],
                      a = !0,
                      l = !1;
                    try {
                      for (
                        n = n.call(e);
                        !(a = (r = n.next()).done) &&
                        (i.push(r.value), !t || i.length !== t);
                        a = !0
                      );
                    } catch (e) {
                      (l = !0), (o = e);
                    } finally {
                      try {
                        a || null == n.return || n.return();
                      } finally {
                        if (l) throw o;
                      }
                    }
                    return i;
                  }
                })(r, o) ||
                (function (e, t) {
                  if (e) {
                    if ("string" == typeof e) return yt(e, t);
                    var n = Object.prototype.toString.call(e).slice(8, -1);
                    return (
                      "Object" === n &&
                        e.constructor &&
                        (n = e.constructor.name),
                      "Map" === n || "Set" === n
                        ? Array.from(e)
                        : "Arguments" === n ||
                          /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)
                        ? yt(e, t)
                        : void 0
                    );
                  }
                })(r, o) ||
                (function () {
                  throw new TypeError(
                    "Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."
                  );
                })()),
            h = m[0],
            b = m[1],
            g = { header: d || 72, body: p || 500 },
            v = u || "30rem",
            y = c || "30rem",
            w = Ce(
              {
                trigger: "click",
                closeOnOutsideClick: !0,
                visible: h,
                offset: [0, 18],
                onVisibleChange: b,
              },
              { placement: f || "top-start" }
            ),
            x = w.getTooltipProps,
            k = w.setTooltipRef,
            E = w.setTriggerRef,
            _ = w.visible,
            S = (function (e, t) {
              var n = [];
              return e && n.concat(e), t && t.tips && (n = n.concat(t.tips)), n;
            })(i, (0, Me.useMephistoTask)().taskConfig),
            T = "".concat(
              s ? "headless-" : "",
              "mephisto-worker-addons-tips__"
            ),
            O = "mephisto-worker-addons-tips__";
          return t().createElement(
            wt,
            { headless: s },
            t().createElement(
              "button",
              {
                ref: E,
                onClick: function () {
                  return b(!h);
                },
                className: "".concat(T, "button ").concat(T, "no-margin"),
              },
              t().createElement(ot, { margin: "0 0.225rem 0 0" }),
              _ ? "Hide Tips" : "Show Tips"
            ),
            _ &&
              t().createElement(
                "div",
                vt({}, x({ className: "tooltip-container" }), {
                  ref: k,
                  className: "".concat(O, "container"),
                }),
                t().createElement(
                  "div",
                  {
                    className: "".concat(O, "padding-container"),
                    style: { maxHeight: v, width: y },
                  },
                  t().createElement(
                    "div",
                    { className: "".concat(T, "task-header-container") },
                    t().createElement(
                      "h1",
                      {
                        style: { margin: 0 },
                        className: "".concat(T, "header1"),
                      },
                      "Task Tips:"
                    ),
                    t().createElement(
                      "button",
                      {
                        onClick: function () {
                          return b(!1);
                        },
                        className: "".concat(T, "close-icon-container"),
                      },
                      t().createElement(gt, null)
                    )
                  ),
                  t().createElement(bt, {
                    tipsArr: S,
                    stylePrefix: T,
                    maxPopupHeight: v,
                  }),
                  !l &&
                    t().createElement(ht, {
                      stylePrefixWithNoHeadlessPrefix: O,
                      stylePrefix: T,
                      handleSubmit: a,
                      maxLengths: g,
                    })
                )
              ),
            t().createElement(
              "style",
              { type: "text/css" },
              '/* Headless Classes */\n\n.headless-mephisto-worker-addons-tips__container {\n  background-color: rgb(245, 245, 245);\n  box-shadow: 10px 10px 33px -8px rgba(0, 0, 0, 0.36);\n  -webkit-box-shadow: 10px 10px 33px -8px rgba(0, 0, 0, 0.36);\n  -moz-box-shadow: 10px 10px 33px -8px rgba(0, 0, 0, 0.36);\n  padding: 0.65rem 1rem;\n  overflow-y: auto;\n  position: absolute;\n}\n.headless-mephisto-worker-addons-tips__no-submissions {\n  margin: 0 0 0 0.75rem !important;\n  font-style: italic;\n}\n\n.headless-mephisto-worker-addons-tips__task-header-container {\n  display: flex;\n  align-items: center;\n  justify-content: space-between;\n}\n\n.headless-mephisto-worker-addons-tips__close-icon-container {\n  background: none;\n  border: 0;\n  padding: 0;\n  cursor: pointer;\n}\n\n.headless-mephisto-worker-addons-tips__list {\n  padding: 0.5rem;\n  margin-bottom: 1.5rem;\n  list-style-type: disc;\n  overflow: auto;\n  border: 2px solid black;\n}\n\n.headless-mephisto-worker-addons-tips__tip {\n  margin: 0 0 1.35rem 1rem;\n}\n\n.headless-mephisto-worker-addons-tips__header2 {\n  margin-bottom: 0.5rem;\n}\n.headless-mephisto-worker-addons-tips__tip:last-child {\n  margin-bottom: 0;\n}\n\n.headless-mephisto-worker-addons-tips__button {\n  margin: 0.75rem 0;\n  display: flex;\n  align-items: center;\n}\n.headless-mephisto-worker-addons-tips__button:disabled {\n  cursor: not-allowed !important;\n}\n.headless-mephisto-worker-addons-tips__label {\n  display: block;\n  cursor: pointer;\n  width: fit-content;\n}\n\n#headless-mephisto-worker-addons-tips__header-input {\n  width: 100%;\n}\n#headless-mephisto-worker-addons-tips__text-input {\n  width: 100%;\n  max-width: 100%;\n  resize: vertical;\n}\n\n/* Non-Headless Classes */\n.mephisto-worker-addons-tips__input-error {\n  box-shadow: 0 0 0 0.25rem rgba(241, 91, 91, 0.65) !important;\n  transition: background-color 200ms, box-shadow 200ms;\n}\n\n.mephisto-worker-addons-tips__list {\n  margin-bottom: 1.5rem;\n  overflow: auto;\n  border: 4px solid #dbdbdb;\n  border-radius: 0.5rem;\n  padding: 0 1rem 0 0;\n  list-style-type: disc;\n}\n.mephisto-worker-addons-tips__header1 {\n  font-weight: bold;\n  font-size: 1.4em;\n  margin: 0.75rem 0;\n}\n\n.mephisto-worker-addons-tips__header2 {\n  font-weight: bold;\n  font-size: 1.125em;\n  margin-bottom: 0.5rem;\n}\n\n.mephisto-worker-addons-tips__tip {\n  margin: 0 0 1.35rem 1.75rem;\n}\n.mephisto-worker-addons-tips__tip:last-child {\n  margin-bottom: 0;\n}\n\n.mephisto-worker-addons-tips__button,\n.mephisto-worker-addons-tips__button:hover,\n.mephisto-worker-addons-tips__button:active,\n.mephisto-worker-addons-tips__button:focus {\n  transition: background-color 200ms, box-shadow 200ms;\n}\n.mephisto-worker-addons-tips__button {\n  margin: 0.75rem 0;\n  padding: 0.65rem 0.75rem;\n  border-radius: 0.5rem;\n  cursor: pointer;\n  border: 0;\n  background-color: rgb(236, 236, 236);\n  font-size: 0.9em;\n  outline: none;\n  display: flex;\n  align-items: center;\n  height: 2.4rem;\n  white-space: nowrap;\n}\n\n.mephisto-worker-addons-tips__task-header-container {\n  display: flex;\n  align-items: center;\n  justify-content: space-between;\n  margin-bottom: 1rem;\n}\n\n.mephisto-worker-addons-tips__close-icon-container {\n  background: none;\n  border: 0;\n  padding: 0;\n  transform: translate(0.5rem, -0.5rem) scale(1);\n  transition: transform 150ms ease-in-out;\n  cursor: pointer;\n}\n\n.mephisto-worker-addons-tips__close-icon-container:hover {\n  transform: translate(0.5rem, -0.5rem) scale(1.1);\n  transition: transform 150ms ease-in-out;\n}\n.mephisto-worker-addons-tips__close-icon-container:active {\n  transform: translate(0.5rem, -0.5rem) scale(0.9);\n  transition: transform 150ms ease-in-out;\n}\n\n.mephisto-worker-addons-tips__button:disabled {\n  cursor: not-allowed !important;\n  color: rgb(164, 164, 164);\n}\n\n.mephisto-worker-addons-tips__button:hover {\n  background-color: rgb(230, 230, 230);\n  box-shadow: 0 0 0 0.1rem rgba(209, 209, 209, 0.5);\n}\n\n.mephisto-worker-addons-tips__button:focus {\n  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.4);\n}\n\n.mephisto-worker-addons-tips__label {\n  display: block;\n  margin: 0.75rem 0;\n  cursor: pointer;\n  width: fit-content;\n}\n\n.mephisto-worker-addons-tips__text {\n  white-space: pre-wrap;\n  font-size: 1em;\n  margin: 0.5rem 0;\n}\n\n#mephisto-worker-addons-tips__header-input,\n#mephisto-worker-addons-tips__text-input {\n  background-color: rgb(240, 240, 240);\n  max-width: 100%;\n  min-height: 2.4rem;\n  height: 2.4rem;\n  max-height: 12rem;\n  box-shadow: 0 0 0 0.15rem rgba(193, 193, 193, 0.5);\n  border: 0;\n  border-radius: 0.35rem;\n  width: 100%;\n  padding: 0.5rem;\n  transition: background-color 200ms, box-shadow 200ms;\n  outline: none;\n  font-family: inherit;\n  font-size: 0.9em;\n  box-sizing: border-box;\n  white-space: pre-wrap;\n  line-height: 1.5;\n  resize: vertical;\n}\n#mephisto-worker-addons-tips__header-input:disabled,\n#mephisto-worker-addons-tips__text-input:disabled {\n  cursor: not-allowed !important;\n}\n\n#mephisto-worker-addons-tips__header-input:hover,\n#mephisto-worker-addons-tips__text-input:hover {\n  background-color: rgb(245, 245, 245);\n  box-shadow: 0 0 0 0.2rem rgba(209, 209, 209, 0.5);\n  transition: background-color 200ms, box-shadow 200ms;\n}\n\n#mephisto-worker-addons-tips__header-input:focus,\n#mephisto-worker-addons-tips__text-input:focus {\n  background-color: rgb(255, 255, 255);\n  transition: background-color 200ms, box-shadow 200ms;\n  box-shadow: 0 0 0 0.25rem rgba(0, 123, 255, 0.5);\n}\n.mephisto-worker-addons-tips__no-submissions {\n  margin: 0.75rem 0 0.75rem 0.75rem !important;\n  color: #565656;\n  font-style: italic;\n}\n\n.mephisto-worker-addons-tips__container {\n  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen,\n    Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;\n  background-color: rgb(245, 245, 245);\n  box-shadow: 10px 10px 33px -8px rgba(0, 0, 0, 0.36);\n  -webkit-box-shadow: 10px 10px 33px -8px rgba(0, 0, 0, 0.36);\n  -moz-box-shadow: 10px 10px 33px -8px rgba(0, 0, 0, 0.36);\n  border-radius: 1.25rem;\n  z-index: 999;\n  line-height: 1.5;\n  color: rgb(70, 70, 70);\n  position: absolute;\n}\n.mephisto-worker-addons-tips__padding-container {\n  padding: 1rem 1.5rem;\n  overflow-y: auto;\n  box-sizing: border-box;\n}\n\n/* Common Classes */\n.mephisto-worker-addons-tips__showing {\n  display: block;\n}\n.mephisto-worker-addons-tips__hiding {\n  display: none;\n}\n\n.mephisto-worker-addons-tips__green-box,\n.mephisto-worker-addons-tips__red-box {\n  padding: 1rem;\n  width: 100%;\n  border-radius: 0.5rem;\n  margin-top: 1rem;\n  box-sizing: border-box;\n}\n\n.mephisto-worker-addons-tips__green-box {\n  background-color: #d1e7dd;\n  color: #315243;\n}\n\n.mephisto-worker-addons-tips__red-box {\n  background-color: #f8d7da;\n  color: #5c3c3f;\n}\n\n.mephisto-worker-addons-tips__loader {\n  width: 21px;\n  height: 21px;\n  border: 3px solid rgb(70, 70, 70);\n  border-bottom-color: transparent;\n  border-radius: 50%;\n  display: inline-block;\n  box-sizing: border-box;\n  animation: mephisto-worker-addons-tips__rotation 1s linear infinite;\n}\n\n@keyframes mephisto-worker-addons-tips__rotation {\n  0% {\n    transform: rotate(0deg);\n  }\n  100% {\n    transform: rotate(360deg);\n  }\n}\n.mephisto-worker-addons-tips__no-margin {\n  margin: 0;\n}\n'
            )
          );
        };
        var kt = r(294),
          Et = {};
        (Et.styleTagTransform = tt()),
          (Et.setAttributes = Xe()),
          (Et.insert = $e().bind(null, "head")),
          (Et.domAPI = Ke()),
          (Et.insertStyleElement = Je()),
          qe()(kt.Z, Et),
          kt.Z && kt.Z.locals && kt.Z.locals;
        const _t = (0, e.forwardRef)(function (e, n) {
          var r = e.width,
            o = e.feedbackText,
            i = e.setFeedbackText,
            a = e.stylePrefix,
            l = e.state,
            s = e.dispatch,
            u = e.maxFeedbackLength,
            c = e.id,
            f = e.containsQuestions,
            d = e.questionsFeedbackText,
            p = e.index,
            m = e.placeholder;
          return t().createElement("textarea", {
            id: c,
            ref: n,
            style: {
              width: "calc(".concat(r, " - 8px)"),
              boxShadow: f ? "" : "10px 10px 23px -15px rgba(0, 0, 0, 0.26)",
            },
            onChange: function (e) {
              !(function (e, t, n) {
                (function (e) {
                  i(e.target.value);
                })(e),
                  t();
              })(e, function () {
                f
                  ? (function (e, t, n, r, o) {
                      for (var i = new Set([]), a = 0; a < o.length; a++)
                        n === a
                          ? e.target.value.length > t
                            ? (console.log("current", e.target.value.length),
                              i.add(a))
                            : i.has(a) && i.remove(a)
                          : o[a].length > t
                          ? (console.log("others", o[a].length), i.add(a))
                          : i.has(a) && i.remove(a);
                      i.size > 0
                        ? r({ type: "multiple-errors", errorIndexes: i })
                        : r({ type: "return-to-default" });
                    })(e, u, p, s, d)
                  : (function (e, t, n, r) {
                      e.target.value.length > t && 4 !== n.status
                        ? r({ type: "too-long" })
                        : e.target.value.length <= t &&
                          r({ type: "return-to-default" });
                    })(e, u, l, s);
              });
            },
            disabled: 1 === l.status,
            value: o,
            placeholder: m || "Enter feedback text here",
            className: ""
              .concat(a, "text-area ")
              .concat(
                (f &&
                  5 === l.status &&
                  l.errorIndexes.has(p) &&
                  a + "text-area-error") ||
                  (!f && 4 === l.status && a + "text-area-error")
              ),
          });
        });
        function St(e, t) {
          (null == t || t > e.length) && (t = e.length);
          for (var n = 0, r = new Array(t); n < t; n++) r[n] = e[n];
          return r;
        }
        const Tt = (0, e.forwardRef)(function (e, n) {
            var r = e.question,
              o = e.index,
              i = e.textAreaWidth,
              a = e.questionsFeedbackText,
              l = e.setQuestionsFeedbackText,
              s = e.stylePrefix,
              u = e.state,
              c = e.dispatch,
              f = e.maxFeedbackLength,
              d = e.placeholder;
            return t().createElement(
              "div",
              {
                className: "".concat(s, "questions-container"),
                key: "question-".concat(o),
              },
              t().createElement(
                "label",
                {
                  className: "".concat(s, "question"),
                  htmlFor: "question-".concat(o),
                },
                r
              ),
              " ",
              t().createElement(_t, {
                id: "question-".concat(o),
                ref: n,
                index: o,
                width: i,
                questionsFeedbackText: a,
                feedbackText: a[o],
                setFeedbackText: function (e) {
                  var t,
                    n =
                      (function (e) {
                        if (Array.isArray(e)) return St(e);
                      })((t = a)) ||
                      (function (e) {
                        if (
                          ("undefined" != typeof Symbol &&
                            null != e[Symbol.iterator]) ||
                          null != e["@@iterator"]
                        )
                          return Array.from(e);
                      })(t) ||
                      (function (e, t) {
                        if (e) {
                          if ("string" == typeof e) return St(e, t);
                          var n = Object.prototype.toString
                            .call(e)
                            .slice(8, -1);
                          return (
                            "Object" === n &&
                              e.constructor &&
                              (n = e.constructor.name),
                            "Map" === n || "Set" === n
                              ? Array.from(e)
                              : "Arguments" === n ||
                                /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(
                                  n
                                )
                              ? St(e, t)
                              : void 0
                          );
                        }
                      })(t) ||
                      (function () {
                        throw new TypeError(
                          "Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."
                        );
                      })();
                  (n[o] = e), l(n);
                },
                stylePrefix: s,
                state: u,
                dispatch: c,
                maxFeedbackLength: f,
                containsQuestions: !0,
                placeholder: d,
              }),
              5 === u.status &&
                u.errorIndexes.has(o) &&
                t().createElement(
                  "div",
                  {
                    className: "mephisto-worker-addons-feedback__red-box",
                    style: { width: i },
                  },
                  u.text
                )
            );
          }),
          Ot = function (e) {
            var n = e.containsQuestions,
              r = e.generalFeedbackText,
              o = e.setGeneralFeedbackText,
              i = e.questionsFeedbackText,
              a = e.setQuestionsFeedbackText,
              l = e.state,
              s = e.dispatch,
              u = e.handleSubmit,
              c = e.stylePrefix,
              f = e.questions,
              d = (0, Me.useMephistoTask)().handleMetadataSubmit;
            return t().createElement(
              "button",
              {
                className: "".concat(c, "button"),
                disabled: lt(n, r, i, l),
                onClick: function () {
                  return (function (e, t, n, r, o, i, a, l, s) {
                    e
                      ? e(r)
                      : (n({ type: "loading" }),
                        t(
                          (function (e, t, n, r) {
                            if (r) {
                              if (
                                !t.every(function (e) {
                                  return e && "string" == typeof e;
                                })
                              )
                                throw new Error(
                                  "A feedback response to one of the questions is not a string"
                                );
                              return {
                                data: n.map(function (e, n) {
                                  return { question: e, text: t[n] };
                                }),
                                type: "feedback",
                              };
                            }
                            if (!e || "string" != typeof e)
                              throw new Error("Feedback text is not a string");
                            return {
                              data: [{ question: "General Feedback", text: e }],
                              type: "feedback",
                            };
                          })(r, i, l, s)
                        )
                          .then(function (e) {
                            "Submitted metadata" === e.status &&
                              (o(""),
                              a(
                                i.map(function () {
                                  return "";
                                })
                              ),
                              n({ type: "success" }),
                              setTimeout(function () {
                                n({ type: "return-to-default" });
                              }, it));
                          })
                          .catch(function (e) {
                            console.error(e),
                              n({ type: "error" }),
                              setTimeout(function () {
                                n({ type: "return-to-default" });
                              }, it);
                          }));
                  })(u, d, s, r, o, i, a, f, n);
                },
              },
              1 === l.status
                ? t().createElement("span", {
                    className: "mephisto-worker-addons-feedback__loader",
                  })
                : "Submit Feedback"
            );
          };
        function Pt() {
          return (
            (Pt = Object.assign
              ? Object.assign.bind()
              : function (e) {
                  for (var t = 1; t < arguments.length; t++) {
                    var n = arguments[t];
                    for (var r in n)
                      Object.prototype.hasOwnProperty.call(n, r) &&
                        (e[r] = n[r]);
                  }
                  return e;
                }),
            Pt.apply(this, arguments)
          );
        }
        function Ct(e, t) {
          return (
            (function (e) {
              if (Array.isArray(e)) return e;
            })(e) ||
            (function (e, t) {
              var n =
                null == e
                  ? null
                  : ("undefined" != typeof Symbol && e[Symbol.iterator]) ||
                    e["@@iterator"];
              if (null != n) {
                var r,
                  o,
                  i = [],
                  a = !0,
                  l = !1;
                try {
                  for (
                    n = n.call(e);
                    !(a = (r = n.next()).done) &&
                    (i.push(r.value), !t || i.length !== t);
                    a = !0
                  );
                } catch (e) {
                  (l = !0), (o = e);
                } finally {
                  try {
                    a || null == n.return || n.return();
                  } finally {
                    if (l) throw o;
                  }
                }
                return i;
              }
            })(e, t) ||
            (function (e, t) {
              if (e) {
                if ("string" == typeof e) return Mt(e, t);
                var n = Object.prototype.toString.call(e).slice(8, -1);
                return (
                  "Object" === n && e.constructor && (n = e.constructor.name),
                  "Map" === n || "Set" === n
                    ? Array.from(e)
                    : "Arguments" === n ||
                      /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)
                    ? Mt(e, t)
                    : void 0
                );
              }
            })(e, t) ||
            (function () {
              throw new TypeError(
                "Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."
              );
            })()
          );
        }
        function Mt(e, t) {
          (null == t || t > e.length) && (t = e.length);
          for (var n = 0, r = new Array(t); n < t; n++) r[n] = e[n];
          return r;
        }
        function Nt(e) {
          var n = e.headless,
            r = e.children;
          return n
            ? t().createElement("div", null, r)
            : t().createElement(Ve.div, null, r);
        }
        const At = function (n) {
          var r = n.headless,
            o = n.questions,
            i = n.handleSubmit,
            a = n.maxTextLength,
            l = n.textAreaWidth,
            s = "".concat(
              r ? "headless-" : "",
              "mephisto-worker-addons-feedback__"
            ),
            u = "mephisto-worker-addons-feedback__",
            c = a || 700,
            f = l || "100%",
            d = Ct((0, e.useState)([]), 2),
            p = d[0],
            m = d[1],
            h = Ct((0, e.useState)(""), 2),
            b = h[0],
            g = h[1],
            v = Ct(
              (0, e.useReducer)(dt, {
                status: 0,
                text: "",
                errorIndexes: null,
              }),
              2
            ),
            y = v[0],
            w = v[1],
            x = (null == o ? void 0 : o.length) > 0,
            k = Ce(
              {
                trigger: null,
                visible: 2 === y.status || 3 === y.status,
                offset: [0, 18],
                onVisibleChange: function () {},
              },
              { placement: "top-start" }
            ),
            E = k.getTooltipProps,
            _ = k.setTooltipRef,
            S = k.setTriggerRef;
          return (
            (0, e.useEffect)(
              function () {
                o &&
                  m(
                    o.map(function () {
                      return "";
                    })
                  );
              },
              [o]
            ),
            t().createElement(
              Nt,
              { headless: r },
              t().createElement(
                "div",
                { className: "".concat(u, "container ").concat(u, "vertical") },
                t().createElement(
                  "header",
                  { className: "".concat(s, "header-items") },
                  t().createElement(
                    "h1",
                    {
                      style: { margin: 0 },
                      className: "".concat(s, "header1"),
                    },
                    "Write Feedback"
                  ),
                  t().createElement(
                    "p",
                    { className: "".concat(s, "subtitle") },
                    " (optional)"
                  )
                ),
                t().createElement(
                  "section",
                  {
                    className: "".concat(
                      s,
                      x ? "items-vertical" : "items-horizontal"
                    ),
                  },
                  x
                    ? o.map(function (e, n) {
                        return t().createElement(Tt, {
                          key: "question-".concat(n),
                          question: e,
                          index: n,
                          ref: S,
                          textAreaWidth: f,
                          questionsFeedbackText: p,
                          setQuestionsFeedbackText: m,
                          stylePrefix: s,
                          state: y,
                          dispatch: w,
                          maxFeedbackLength: c,
                          containsQuestions: x,
                          placeholder: "Answer the above question here",
                        });
                      })
                    : t().createElement(_t, {
                        id: "".concat(u, "solo-input"),
                        ref: S,
                        width: f,
                        feedbackText: b,
                        setFeedbackText: g,
                        stylePrefix: s,
                        state: y,
                        dispatch: w,
                        maxFeedbackLength: c,
                        containsQuestions: x,
                      }),
                  ((!x && 2 === y.status) ||
                    3 === y.status ||
                    4 === y.status) &&
                    t().createElement(
                      "div",
                      Pt({}, E({ className: "tooltip-container" }), {
                        ref: _,
                        className: ""
                          .concat(s)
                          .concat(2 === y.status ? "green" : "red", "-box"),
                      }),
                      y.text
                    ),
                  t().createElement(Ot, {
                    containsQuestions: x,
                    questions: o,
                    generalFeedbackText: b,
                    setGeneralFeedbackText: g,
                    questionsFeedbackText: p,
                    setQuestionsFeedbackText: m,
                    state: y,
                    dispatch: w,
                    handleSubmit: i,
                    stylePrefix: s,
                  }),
                  x &&
                    2 === y.status &&
                    t().createElement(
                      "div",
                      {
                        className: "".concat(u, "green-box"),
                        style: { width: f },
                      },
                      y.text
                    )
                )
              ),
              t().createElement(
                "style",
                { type: "text/css" },
                '/* Headless Classes */\n.headless-mephisto-worker-addons-feedback__question {\n  display: block;\n  cursor: pointer;\n  overflow-wrap: break-word;\n}\n.headless-mephisto-worker-addons-feedback__header-items {\n  display: flex;\n  align-items: center;\n  flex-wrap: wrap;\n}\n\n.headless-mephisto-worker-addons-feedback__green-box,\n.headless-mephisto-worker-addons-feedback__red-box {\n  padding: 1rem;\n  width: min(18rem, 100%);\n  box-sizing: border-box;\n}\n\n.headless-mephisto-worker-addons-feedback__green-box {\n  background-color: #d1e7dd;\n  color: #315243;\n}\n\n.headless-mephisto-worker-addons-feedback__red-box {\n  background-color: #f8d7da;\n  color: #5c3c3f;\n}\n.headless-mephisto-worker-addons-feedback__items-horizontal {\n  display: flex;\n  align-items: center;\n}\n.headless-mephisto-worker-addons-feedback__subtitle {\n  font-style: italic;\n  font-size: 0.85em;\n  margin: 0;\n}\n\n/* Non-Headless Classes */\n.mephisto-worker-addons-feedback__button,\n.mephisto-worker-addons-feedback__button:hover,\n.mephisto-worker-addons-feedback__button:active,\n.mephisto-worker-addons-feedback__button:focus {\n  transition: background-color 200ms, box-shadow 200ms;\n}\n.mephisto-worker-addons-feedback__button {\n  padding: 0.65rem 0.75rem;\n  border-radius: 0.5rem;\n  cursor: pointer;\n  border: 0;\n  background-color: rgb(236, 236, 236);\n  font-size: 0.9em;\n  outline: none;\n  display: flex;\n  align-items: center;\n  min-height: 2.75rem;\n  width: fit-content;\n  margin: 0.5rem 0.25rem;\n}\n\n.mephisto-worker-addons-feedback__button:disabled {\n  cursor: not-allowed !important;\n  color: #969696;\n}\n\n.mephisto-worker-addons-feedback__button:hover {\n  background-color: rgb(230, 230, 230);\n  box-shadow: 0 0 0 0.1rem rgba(209, 209, 209, 0.5);\n}\n\n.mephisto-worker-addons-feedback__button:focus {\n  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.4);\n}\n\n.mephisto-worker-addons-feedback__question {\n  margin-bottom: 0.25rem;\n  display: block;\n  cursor: pointer;\n  overflow-wrap: break-word;\n  width: fit-content;\n}\n.mephisto-worker-addons-feedback__header1 {\n  font-weight: bold;\n  font-size: 1.4em;\n  margin: 0.75rem 0;\n}\n\n.mephisto-worker-addons-feedback__subtitle {\n  font-style: italic;\n  font-size: 0.85em;\n  color: rgb(97, 97, 97);\n  margin: 0 0 0 0.175rem;\n}\n\n.mephisto-worker-addons-feedback__header-items {\n  display: flex;\n  align-items: center;\n  margin-bottom: 0.75rem;\n  flex-wrap: wrap;\n}\n\n.mephisto-worker-addons-feedback__green-box,\n.mephisto-worker-addons-feedback__red-box {\n  padding: 1rem;\n  width: min(18rem, 100%);\n  border-radius: 0.5rem;\n  margin: 1rem 0 0.75rem;\n  box-sizing: border-box;\n}\n\n.mephisto-worker-addons-feedback__green-box {\n  background-color: #d1e7dd;\n  color: #315243;\n}\n\n.mephisto-worker-addons-feedback__red-box {\n  background-color: #f8d7da;\n  color: #5c3c3f;\n}\n\n/* Common Classes */\n.mephisto-worker-addons-feedback__container {\n  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen,\n    Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;\n  display: flex;\n  align-items: flex-start;\n  justify-content: flex-start;\n  background-color: rgb(245, 245, 245);\n  padding: 1.5rem;\n  border-radius: 1rem;\n  line-height: 1.5;\n  color: rgb(70, 70, 70);\n}\n\n.mephisto-worker-addons-feedback__questions-container {\n  margin-bottom: 0.5rem;\n}\n.mephisto-worker-addons-feedback__items-horizontal {\n  display: flex;\n  width: 100%;\n  flex-wrap: wrap;\n}\n\n.mephisto-worker-addons-feedback__items-vertical {\n  display: flex;\n  flex-direction: column;\n  width: 100%;\n}\n.mephisto-worker-addons-feedback__text-area:disabled {\n  cursor: not-allowed !important;\n}\n.mephisto-worker-addons-feedback__text-area {\n  min-width: min(8rem, 100%);\n  max-width: 100%;\n  min-height: 2.4rem;\n  height: 2.4rem;\n  max-height: 12rem;\n  background-color: rgb(240, 240, 240);\n  box-shadow: 0 0 0 0.15rem rgba(193, 193, 193, 0.5);\n  border: 0;\n  border-radius: 0.35rem;\n  padding: 0.5rem;\n  transition: background-color 200ms, box-shadow 200ms;\n  outline: none;\n  font-family: inherit;\n  font-size: 0.9em;\n  box-sizing: border-box;\n  transform: translateY(2.2px);\n  resize: vertical;\n  line-height: 1.5;\n  flex: 1;\n  margin: 0.5rem 0.25rem;\n}\n\n.mephisto-worker-addons-feedback__text-area-error {\n  box-shadow: 0 0 0 0.25rem rgba(241, 91, 91, 0.65) !important;\n  transition: background-color 200ms, box-shadow 200ms;\n}\n\n.mephisto-worker-addons-feedback__content-container {\n  margin: 0 0 1rem;\n  width: 100%;\n}\n.mephisto-worker-addons-feedback__text-area:hover {\n  background-color: rgb(245, 245, 245);\n  box-shadow: 0 0 0 0.2rem rgba(209, 209, 209, 0.5);\n  transition: background-color 200ms, box-shadow 200ms;\n}\n\n.mephisto-worker-addons-feedback__text-area:focus {\n  background-color: rgb(255, 255, 255);\n  transition: background-color 200ms, box-shadow 200ms;\n  box-shadow: 0 0 0 0.25rem rgba(0, 123, 255, 0.5);\n}\n\n.mephisto-worker-addons-feedback__vertical {\n  flex-direction: column;\n  align-items: flex-start;\n}\n\n.mephisto-worker-addons-feedback__loader {\n  width: 21px;\n  height: 21px;\n  border: 3px solid rgb(83, 83, 83);\n  border-bottom-color: transparent;\n  border-radius: 50%;\n  display: inline-block;\n  box-sizing: border-box;\n  animation: rotation 1s linear infinite;\n}\n@keyframes rotation {\n  0% {\n    transform: rotate(0deg);\n  }\n  100% {\n    transform: rotate(360deg);\n  }\n}\n'
              )
            )
          );
        };
      })(),
      o
    );
  })()
);
