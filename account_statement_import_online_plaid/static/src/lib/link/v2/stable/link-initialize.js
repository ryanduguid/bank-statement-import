var Plaid = (function (e) {
  function webpackJsonpCallback(t) {
    for (var r, o, i = t[0], s = t[1], u = 0, c = []; u < i.length; u++)
      (o = i[u]),
        Object.prototype.hasOwnProperty.call(n, o) && n[o] && c.push(n[o][0]),
        (n[o] = 0);
    for (r in s) Object.prototype.hasOwnProperty.call(s, r) && (e[r] = s[r]);
    for (a && a(t); c.length; ) c.shift()();
  }
  var t = {},
    n = {45: 0};
  function __webpack_require__(n) {
    if (t[n]) return t[n].exports;
    var r = (t[n] = {i: n, l: !1, exports: {}});
    return (
      e[n].call(r.exports, r, r.exports, __webpack_require__), (r.l = !0), r.exports
    );
  }
  (__webpack_require__.e = function requireEnsure(e) {
    var t = [],
      r = n[e];
    if (0 !== r)
      if (r) t.push(r[2]);
      else {
        var o = new Promise(function (t, o) {
          r = n[e] = [t, o];
        });
        t.push((r[2] = o));
        var i,
          a = document.createElement("script");
        (a.charset = "utf-8"),
          (a.timeout = 120),
          __webpack_require__.nc && a.setAttribute("nonce", __webpack_require__.nc),
          (a.src = (function jsonpScriptSrc(e) {
            return (
              __webpack_require__.p +
              "" +
              ({
                7: "vendors~CBWalletWeb3~ethers",
                8: "vendors~WCV2Web3~WCWeb3",
                9: "vendors~chainUtilities~web3Bridge",
                19: "CBWalletWeb3",
                20: "CBWalletWeb3Storage",
                34: "WCV2Web3",
                35: "WCWeb3",
                37: "chainUtilities",
                41: "ethers",
                54: "vendors~CBWalletWeb3",
                56: "vendors~WCV2Web3",
                57: "vendors~WCWeb3",
                58: "vendors~ethers",
                61: "vendors~web3Bridge",
                62: "web3Bridge",
              }[e] || e) +
              ".js"
            );
          })(e));
        var s = new Error();
        i = function (t) {
          (a.onerror = a.onload = null), clearTimeout(u);
          var r = n[e];
          if (0 !== r) {
            if (r) {
              var o = t && ("load" === t.type ? "missing" : t.type),
                i = t && t.target && t.target.src;
              (s.message = "Loading chunk " + e + " failed.\n(" + o + ": " + i + ")"),
                (s.name = "ChunkLoadError"),
                (s.type = o),
                (s.request = i),
                r[1](s);
            }
            n[e] = void 0;
          }
        };
        var u = setTimeout(function () {
          i({type: "timeout", target: a});
        }, 12e4);
        (a.onerror = a.onload = i), document.head.appendChild(a);
      }
    return Promise.all(t);
  }),
    (__webpack_require__.m = e),
    (__webpack_require__.c = t),
    (__webpack_require__.d = function (e, t, n) {
      __webpack_require__.o(e, t) ||
        Object.defineProperty(e, t, {enumerable: !0, get: n});
    }),
    (__webpack_require__.r = function (e) {
      "undefined" != typeof Symbol &&
        Symbol.toStringTag &&
        Object.defineProperty(e, Symbol.toStringTag, {value: "Module"}),
        Object.defineProperty(e, "__esModule", {value: !0});
    }),
    (__webpack_require__.t = function (e, t) {
      if ((1 & t && (e = __webpack_require__(e)), 8 & t)) return e;
      if (4 & t && "object" == typeof e && e && e.__esModule) return e;
      var n = Object.create(null);
      if (
        (__webpack_require__.r(n),
        Object.defineProperty(n, "default", {enumerable: !0, value: e}),
        2 & t && "string" != typeof e)
      )
        for (var r in e)
          __webpack_require__.d(
            n,
            r,
            function (t) {
              return e[t];
            }.bind(null, r)
          );
      return n;
    }),
    (__webpack_require__.n = function (e) {
      var t =
        e && e.__esModule
          ? function getDefault() {
              return e.default;
            }
          : function getModuleExports() {
              return e;
            };
      return __webpack_require__.d(t, "a", t), t;
    }),
    (__webpack_require__.o = function (e, t) {
      return Object.prototype.hasOwnProperty.call(e, t);
    }),
    (__webpack_require__.p = "/link/2.0.3119/"),
    (__webpack_require__.oe = function (e) {
      throw (console.error(e), e);
    });
  var r = (window.webpackJsonpPlaid = window.webpackJsonpPlaid || []),
    o = r.push.bind(r);
  (r.push = webpackJsonpCallback), (r = r.slice());
  for (var i = 0; i < r.length; i++) webpackJsonpCallback(r[i]);
  var a = o;
  return __webpack_require__((__webpack_require__.s = 4522));
})({
  101: function (e, t, n) {
    "use strict";
    var r = n(20),
      o = n(23),
      aFunction = function (e) {
        return o(e) ? e : void 0;
      };
    e.exports = function (e, t) {
      return arguments.length < 2 ? aFunction(r[e]) : r[e] && r[e][t];
    };
  },
  107: function (e, t, n) {
    "use strict";
    var r = n(30),
      o = n(78),
      i = n(141);
    e.exports = r
      ? function (e, t, n) {
          return o.f(e, t, i(1, n));
        }
      : function (e, t, n) {
          return (e[t] = n), e;
        };
  },
  113: function (e, t, n) {
    "use strict";
    var r = n(399),
      o = n(68),
      i = n(188),
      a = r(r.bind);
    e.exports = function (e, t) {
      return (
        o(e),
        void 0 === t
          ? e
          : i
            ? a(e, t)
            : function () {
                return e.apply(t, arguments);
              }
      );
    };
  },
  114: function (e, t, n) {
    "use strict";
    Object.defineProperty(t, "__esModule", {value: !0});
    var r = {
      API_VERSIONS: !0,
      EXTERNAL_ENVIRONMENTS_API_V1: !0,
      INTERNAL_ENVIRONMENTS_API_V1: !0,
      EXTERNAL_ENVIRONMENTS_API_V2: !0,
      VERSION: !0,
      INTERNAL_ENVIRONMENTS_API_V2: !0,
      ENVIRONMENTS_TO_DOMAIN: !0,
      PLAID_WEBVIEW_NAMESPACE: !0,
      PAYMENT_INITIATION: !0,
      PRODUCTS_API_V1: !0,
      PRODUCTS_API_V2_ONLY: !0,
      PRODUCTS_API_V2: !0,
      PRODUCTS_API_V2_BETA: !0,
      I18N_SUPPORTED_LANGUAGES: !0,
      DEFAULT_LANGUAGE: !0,
      FLEXIBLE_INPUT_OVERWRITE_STATUSES: !0,
      CLOUDFLARE_ETH_MAINNET_URL: !0,
      MAINNET_HEX_CHAIN_ID: !0,
      PLAID_LINK_BUTTON_ID: !0,
      PLAID_FLOW_INTERNAL_NAMESPACE: !0,
      PLAID_INTERNAL_NAMESPACE: !0,
      CREATE_PARAMETERS: !0,
    };
    (t.CLOUDFLARE_ETH_MAINNET_URL = t.API_VERSIONS = void 0),
      Object.defineProperty(t, "CREATE_PARAMETERS", {
        enumerable: !0,
        get: function () {
          return o.CREATE_PARAMETERS;
        },
      }),
      (t.PLAID_FLOW_INTERNAL_NAMESPACE =
        t.PAYMENT_INITIATION =
        t.MAINNET_HEX_CHAIN_ID =
        t.INTERNAL_ENVIRONMENTS_API_V2 =
        t.INTERNAL_ENVIRONMENTS_API_V1 =
        t.I18N_SUPPORTED_LANGUAGES =
        t.FLEXIBLE_INPUT_OVERWRITE_STATUSES =
        t.EXTERNAL_ENVIRONMENTS_API_V2 =
        t.EXTERNAL_ENVIRONMENTS_API_V1 =
        t.ENVIRONMENTS_TO_DOMAIN =
        t.DEFAULT_LANGUAGE =
          void 0),
      Object.defineProperty(t, "PLAID_INTERNAL_NAMESPACE", {
        enumerable: !0,
        get: function () {
          return o.PLAID_INTERNAL_NAMESPACE;
        },
      }),
      (t.VERSION =
        t.PRODUCTS_API_V2_ONLY =
        t.PRODUCTS_API_V2_BETA =
        t.PRODUCTS_API_V2 =
        t.PRODUCTS_API_V1 =
        t.PLAID_WEBVIEW_NAMESPACE =
        t.PLAID_LINK_BUTTON_ID =
          void 0);
    var o = n(364);
    Object.keys(o).forEach(function (e) {
      "default" !== e &&
        "__esModule" !== e &&
        (Object.prototype.hasOwnProperty.call(r, e) ||
          (e in t && t[e] === o[e]) ||
          Object.defineProperty(t, e, {
            enumerable: !0,
            get: function () {
              return o[e];
            },
          }));
    });
    t.API_VERSIONS = ["v1", "v2"];
    t.EXTERNAL_ENVIRONMENTS_API_V1 = ["tartan", "production"];
    t.INTERNAL_ENVIRONMENTS_API_V1 = ["testing", "tartan", "production"];
    t.EXTERNAL_ENVIRONMENTS_API_V2 = ["sandbox", "development", "production"];
    const i = String("2.0.3119");
    t.VERSION = i;
    t.INTERNAL_ENVIRONMENTS_API_V2 = [
      "end2end",
      "devenv",
      "testing",
      "sandbox",
      "development",
      "production",
    ];
    t.ENVIRONMENTS_TO_DOMAIN = {
      devenv: "http://localhost:8082",
      testing: "https://apiv2-testing.plaid.io",
      tartan: "https://development.plaid.com",
      development: "https://development.plaid.com",
      sandbox: "https://sandbox.plaid.com",
      production: "https://production.plaid.com",
    };
    t.PLAID_WEBVIEW_NAMESPACE = "plaidlink";
    const a = "payment_initiation";
    t.PAYMENT_INITIATION = a;
    t.PRODUCTS_API_V1 = ["auth", "connect", "income", "info"];
    const s = [
      "account_verify",
      "assets",
      "bank_transfer",
      "transfer",
      "ddta",
      "deposit_switch",
      "holdings",
      "income_verification",
      "investments_auth",
      "investments",
      "liabilities",
      a,
      "sba_verification",
      "liabilities_report",
    ];
    t.PRODUCTS_API_V2_ONLY = s;
    const u = [
      "account_verify",
      "assets",
      "auth",
      "transfer",
      "bank_transfer",
      "ddta",
      "deposit_switch",
      "holdings",
      "identity",
      "income",
      "income_verification",
      "investments_auth",
      "investments",
      "liabilities",
      a,
      "transactions",
      "sba_verification",
      "liabilities_report",
    ];
    t.PRODUCTS_API_V2 = u;
    const c = [
      "account_verify",
      "bank_transfer",
      "transfer",
      "holdings",
      "investments_auth",
      "ddta",
      a,
      "deposit_switch",
      "sba_verification",
      "liabilities_report",
      "income_verification",
    ];
    t.PRODUCTS_API_V2_BETA = c;
    t.I18N_SUPPORTED_LANGUAGES = ["en", "es", "fr"];
    t.DEFAULT_LANGUAGE = "en";
    t.FLEXIBLE_INPUT_OVERWRITE_STATUSES = ["choose_device"];
    t.CLOUDFLARE_ETH_MAINNET_URL = "https://cloudflare-eth.com/v1/mainnet";
    t.MAINNET_HEX_CHAIN_ID = "0x1";
    t.PLAID_LINK_BUTTON_ID = "plaid-link-button";
    t.PLAID_FLOW_INTERNAL_NAMESPACE = "plaid_flow";
  },
  121: function (e, t, n) {
    "use strict";
    var r = n(21);
    e.exports = r({}.isPrototypeOf);
  },
  122: function (e, t, n) {
    "use strict";
    var r = n(78).f,
      o = n(45),
      i = n(27)("toStringTag");
    e.exports = function (e, t, n) {
      e && !n && (e = e.prototype),
        e && !o(e, i) && r(e, i, {configurable: !0, value: t});
    };
  },
  123: function (e, t, n) {
    "use strict";
    var r,
      o = n(55),
      i = n(489),
      a = n(253),
      s = n(252),
      u = n(344),
      c = n(198),
      l = n(251),
      d = l("IE_PROTO"),
      EmptyConstructor = function () {},
      scriptTag = function (e) {
        return "<script>" + e + "</" + "script>";
      },
      NullProtoObjectViaActiveX = function (e) {
        e.write(scriptTag("")), e.close();
        var t = e.parentWindow.Object;
        return (e = null), t;
      },
      NullProtoObject = function () {
        try {
          r = new ActiveXObject("htmlfile");
        } catch (e) {}
        var e, t;
        NullProtoObject =
          "undefined" != typeof document
            ? document.domain && r
              ? NullProtoObjectViaActiveX(r)
              : (((t = c("iframe")).style.display = "none"),
                u.appendChild(t),
                (t.src = String("javascript:")),
                (e = t.contentWindow.document).open(),
                e.write(scriptTag("document.F=Object")),
                e.close(),
                e.F)
            : NullProtoObjectViaActiveX(r);
        for (var n = a.length; n--; ) delete NullProtoObject.prototype[a[n]];
        return NullProtoObject();
      };
    (s[d] = !0),
      (e.exports =
        Object.create ||
        function create(e, t) {
          var n;
          return (
            null !== e
              ? ((EmptyConstructor.prototype = o(e)),
                (n = new EmptyConstructor()),
                (EmptyConstructor.prototype = null),
                (n[d] = e))
              : (n = NullProtoObject()),
            void 0 === t ? n : i.f(n, t)
          );
        });
  },
  124: function (e, t, n) {
    "use strict";
    e.exports = ("undefined" != typeof navigator && String(navigator.userAgent)) || "";
  },
  13: function (e, t, n) {
    "use strict";
    var r = n(29),
      o = n(254);
    r({target: "RegExp", proto: !0, forced: /./.exec !== o}, {exec: o});
  },
  131: function (e, t, n) {
    "use strict";
    var r = n(488);
    e.exports = function (e) {
      var t = +e;
      return t != t || 0 === t ? 0 : r(t);
    };
  },
  132: function (e, t) {
    var n;
    n = (function () {
      return this;
    })();
    try {
      n = n || new Function("return this")();
    } catch (e) {
      "object" == typeof window && (n = window);
    }
    e.exports = n;
  },
  135: function (e, t, n) {
    "use strict";
    var r = n(324),
      o = n(78);
    e.exports = function (e, t, n) {
      return (
        n.get && r(n.get, t, {getter: !0}),
        n.set && r(n.set, t, {setter: !0}),
        o.f(e, t, n)
      );
    };
  },
  139: function (e, t, n) {
    "use strict";
    var r = n(413),
      o = n(23),
      i = n(90),
      a = n(27)("toStringTag"),
      s = Object,
      u =
        "Arguments" ===
        i(
          (function () {
            return arguments;
          })()
        );
    e.exports = r
      ? i
      : function (e) {
          var t, n, r;
          return void 0 === e
            ? "Undefined"
            : null === e
              ? "Null"
              : "string" ==
                  typeof (n = (function (e, t) {
                    try {
                      return e[t];
                    } catch (e) {}
                  })((t = s(e)), a))
                ? n
                : u
                  ? i(t)
                  : "Object" === (r = i(t)) && o(t.callee)
                    ? "Arguments"
                    : r;
        };
  },
  141: function (e, t, n) {
    "use strict";
    e.exports = function (e, t) {
      return {
        enumerable: !(1 & e),
        configurable: !(2 & e),
        writable: !(4 & e),
        value: t,
      };
    };
  },
  148: function (e, t, n) {
    "use strict";
    var r = n(29),
      o = n(21),
      i = n(68),
      a = n(84),
      s = n(89),
      u = n(552),
      c = n(80),
      l = n(22),
      d = n(298),
      f = n(316),
      p = n(437),
      v = n(438),
      _ = n(176),
      y = n(439),
      h = [],
      g = o(h.sort),
      b = o(h.push),
      E = l(function () {
        h.sort(void 0);
      }),
      m = l(function () {
        h.sort(null);
      }),
      w = f("sort"),
      O = !l(function () {
        if (_) return _ < 70;
        if (!(p && p > 3)) {
          if (v) return !0;
          if (y) return y < 603;
          var e,
            t,
            n,
            r,
            o = "";
          for (e = 65; e < 76; e++) {
            switch (((t = String.fromCharCode(e)), e)) {
              case 66:
              case 69:
              case 70:
              case 72:
                n = 3;
                break;
              case 68:
              case 71:
                n = 4;
                break;
              default:
                n = 2;
            }
            for (r = 0; r < 47; r++) h.push({k: t + r, v: n});
          }
          for (
            h.sort(function (e, t) {
              return t.v - e.v;
            }),
              r = 0;
            r < h.length;
            r++
          )
            (t = h[r].k.charAt(0)), o.charAt(o.length - 1) !== t && (o += t);
          return "DGBEFHACIJK" !== o;
        }
      });
    r(
      {target: "Array", proto: !0, forced: E || !m || !w || !O},
      {
        sort: function sort(e) {
          void 0 !== e && i(e);
          var t = a(this);
          if (O) return void 0 === e ? g(t) : g(t, e);
          var n,
            r,
            o = [],
            l = s(t);
          for (r = 0; r < l; r++) r in t && b(o, t[r]);
          for (
            d(
              o,
              (function (e) {
                return function (t, n) {
                  return void 0 === n
                    ? -1
                    : void 0 === t
                      ? 1
                      : void 0 !== e
                        ? +e(t, n) || 0
                        : c(t) > c(n)
                          ? 1
                          : -1;
                };
              })(e)
            ),
              n = s(o),
              r = 0;
            r < n;

          )
            t[r] = o[r++];
          for (; r < l; ) u(t, r++);
          return t;
        },
      }
    );
  },
  149: function (e, t, n) {
    "use strict";
    var r = n(159),
      o = TypeError;
    e.exports = function (e) {
      if (r(e)) throw new o("Can't call method on " + e);
      return e;
    };
  },
  153: function (e, t, n) {
    "use strict";
    var r = String;
    e.exports = function (e) {
      try {
        return r(e);
      } catch (e) {
        return "Object";
      }
    };
  },
  157: function (e, t, n) {
    "use strict";
    var r = n(208),
      o = n(149);
    e.exports = function (e) {
      return r(o(e));
    };
  },
  159: function (e, t, n) {
    "use strict";
    e.exports = function (e) {
      return null == e;
    };
  },
  160: function (e, t, n) {
    "use strict";
    e.exports = {};
  },
  161: function (e, t, n) {
    "use strict";
    var r = n(20),
      o = n(90);
    e.exports = "process" === o(r.process);
  },
  176: function (e, t, n) {
    "use strict";
    var r,
      o,
      i = n(20),
      a = n(124),
      s = i.process,
      u = i.Deno,
      c = (s && s.versions) || (u && u.version),
      l = c && c.v8;
    l && (o = (r = l.split("."))[0] > 0 && r[0] < 4 ? 1 : +(r[0] + r[1])),
      !o &&
        a &&
        (!(r = a.match(/Edge\/(\d+)/)) || r[1] >= 74) &&
        (r = a.match(/Chrome\/(\d+)/)) &&
        (o = +r[1]),
      (e.exports = o);
  },
  178: function (e, t, n) {
    "use strict";
    var r = n(493),
      o = n(51),
      i = n(149),
      a = n(494);
    e.exports =
      Object.setPrototypeOf ||
      ("__proto__" in {}
        ? (function () {
            var e,
              t = !1,
              n = {};
            try {
              (e = r(Object.prototype, "__proto__", "set"))(n, []),
                (t = n instanceof Array);
            } catch (e) {}
            return function setPrototypeOf(n, r) {
              return i(n), a(r), o(n) ? (t ? e(n, r) : (n.__proto__ = r), n) : n;
            };
          })()
        : void 0);
  },
  184: function (e, t, n) {
    "use strict";
    var r = n(139),
      o = n(197),
      i = n(159),
      a = n(160),
      s = n(27)("iterator");
    e.exports = function (e) {
      if (!i(e)) return o(e, s) || o(e, "@@iterator") || a[r(e)];
    };
  },
  185: function (e, t, n) {
    "use strict";
    var r = n(21);
    e.exports = r([].slice);
  },
  188: function (e, t, n) {
    "use strict";
    var r = n(22);
    e.exports = !r(function () {
      var e = function () {}.bind();
      return "function" != typeof e || e.hasOwnProperty("prototype");
    });
  },
  197: function (e, t, n) {
    "use strict";
    var r = n(68),
      o = n(159);
    e.exports = function (e, t) {
      var n = e[t];
      return o(n) ? void 0 : r(n);
    };
  },
  198: function (e, t, n) {
    "use strict";
    var r = n(20),
      o = n(51),
      i = r.document,
      a = o(i) && o(i.createElement);
    e.exports = function (e) {
      return a ? i.createElement(e) : {};
    };
  },
  2: function (e, t, n) {
    "use strict";
    var r = n(157),
      o = n(271),
      i = n(160),
      a = n(81),
      s = n(78).f,
      u = n(345),
      c = n(266),
      l = n(92),
      d = n(30),
      f = "Array Iterator",
      p = a.set,
      v = a.getterFor(f);
    e.exports = u(
      Array,
      "Array",
      function (e, t) {
        p(this, {type: f, target: r(e), index: 0, kind: t});
      },
      function () {
        var e = v(this),
          t = e.target,
          n = e.index++;
        if (!t || n >= t.length) return (e.target = void 0), c(void 0, !0);
        switch (e.kind) {
          case "keys":
            return c(n, !1);
          case "values":
            return c(t[n], !1);
        }
        return c([n, t[n]], !1);
      },
      "values"
    );
    var _ = (i.Arguments = i.Array);
    if ((o("keys"), o("values"), o("entries"), !l && d && "values" !== _.name))
      try {
        s(_, "name", {value: "values"});
      } catch (e) {}
  },
  20: function (e, t, n) {
    "use strict";
    (function (t) {
      var check = function (e) {
        return e && e.Math === Math && e;
      };
      e.exports =
        check("object" == typeof globalThis && globalThis) ||
        check("object" == typeof window && window) ||
        check("object" == typeof self && self) ||
        check("object" == typeof t && t) ||
        check("object" == typeof this && this) ||
        (function () {
          return this;
        })() ||
        Function("return this")();
    }).call(this, n(132));
  },
  207: function (e, t, n) {
    "use strict";
    var r = n(121),
      o = TypeError;
    e.exports = function (e, t) {
      if (r(t, e)) return e;
      throw new o("Incorrect invocation");
    };
  },
  208: function (e, t, n) {
    "use strict";
    var r = n(21),
      o = n(22),
      i = n(90),
      a = Object,
      s = r("".split);
    e.exports = o(function () {
      return !a("z").propertyIsEnumerable(0);
    })
      ? function (e) {
          return "String" === i(e) ? s(e, "") : a(e);
        }
      : a;
  },
  21: function (e, t, n) {
    "use strict";
    var r = n(188),
      o = Function.prototype,
      i = o.call,
      a = r && o.bind.bind(i, i);
    e.exports = r
      ? a
      : function (e) {
          return function () {
            return i.apply(e, arguments);
          };
        };
  },
  216: function (e, t, n) {
    "use strict";
    var r = n(101),
      o = n(23),
      i = n(121),
      a = n(321),
      s = Object;
    e.exports = a
      ? function (e) {
          return "symbol" == typeof e;
        }
      : function (e) {
          var t = r("Symbol");
          return o(t) && i(t.prototype, s(e));
        };
  },
  22: function (e, t, n) {
    "use strict";
    e.exports = function (e) {
      try {
        return !!e();
      } catch (e) {
        return !0;
      }
    };
  },
  220: function (e, t) {
    var n,
      r,
      o = (e.exports = {});
    function defaultSetTimout() {
      throw new Error("setTimeout has not been defined");
    }
    function defaultClearTimeout() {
      throw new Error("clearTimeout has not been defined");
    }
    function runTimeout(e) {
      if (n === setTimeout) return setTimeout(e, 0);
      if ((n === defaultSetTimout || !n) && setTimeout)
        return (n = setTimeout), setTimeout(e, 0);
      try {
        return n(e, 0);
      } catch (t) {
        try {
          return n.call(null, e, 0);
        } catch (t) {
          return n.call(this, e, 0);
        }
      }
    }
    !(function () {
      try {
        n = "function" == typeof setTimeout ? setTimeout : defaultSetTimout;
      } catch (e) {
        n = defaultSetTimout;
      }
      try {
        r = "function" == typeof clearTimeout ? clearTimeout : defaultClearTimeout;
      } catch (e) {
        r = defaultClearTimeout;
      }
    })();
    var i,
      a = [],
      s = !1,
      u = -1;
    function cleanUpNextTick() {
      s &&
        i &&
        ((s = !1), i.length ? (a = i.concat(a)) : (u = -1), a.length && drainQueue());
    }
    function drainQueue() {
      if (!s) {
        var e = runTimeout(cleanUpNextTick);
        s = !0;
        for (var t = a.length; t; ) {
          for (i = a, a = []; ++u < t; ) i && i[u].run();
          (u = -1), (t = a.length);
        }
        (i = null),
          (s = !1),
          (function runClearTimeout(e) {
            if (r === clearTimeout) return clearTimeout(e);
            if ((r === defaultClearTimeout || !r) && clearTimeout)
              return (r = clearTimeout), clearTimeout(e);
            try {
              return r(e);
            } catch (t) {
              try {
                return r.call(null, e);
              } catch (t) {
                return r.call(this, e);
              }
            }
          })(e);
      }
    }
    function Item(e, t) {
      (this.fun = e), (this.array = t);
    }
    function noop() {}
    (o.nextTick = function (e) {
      var t = new Array(arguments.length - 1);
      if (arguments.length > 1)
        for (var n = 1; n < arguments.length; n++) t[n - 1] = arguments[n];
      a.push(new Item(e, t)), 1 !== a.length || s || runTimeout(drainQueue);
    }),
      (Item.prototype.run = function () {
        this.fun.apply(null, this.array);
      }),
      (o.title = "browser"),
      (o.browser = !0),
      (o.env = {}),
      (o.argv = []),
      (o.version = ""),
      (o.versions = {}),
      (o.on = noop),
      (o.addListener = noop),
      (o.once = noop),
      (o.off = noop),
      (o.removeListener = noop),
      (o.removeAllListeners = noop),
      (o.emit = noop),
      (o.prependListener = noop),
      (o.prependOnceListener = noop),
      (o.listeners = function (e) {
        return [];
      }),
      (o.binding = function (e) {
        throw new Error("process.binding is not supported");
      }),
      (o.cwd = function () {
        return "/";
      }),
      (o.chdir = function (e) {
        throw new Error("process.chdir is not supported");
      }),
      (o.umask = function () {
        return 0;
      });
  },
  229: function (e, t, n) {
    "use strict";
    var r = n(131),
      o = Math.min;
    e.exports = function (e) {
      var t = r(e);
      return t > 0 ? o(t, 9007199254740991) : 0;
    };
  },
  23: function (e, t, n) {
    "use strict";
    var r = "object" == typeof document && document.all;
    e.exports =
      void 0 === r && void 0 !== r
        ? function (e) {
            return "function" == typeof e || e === r;
          }
        : function (e) {
            return "function" == typeof e;
          };
  },
  231: function (e, t, n) {
    "use strict";
    var r = n(28),
      o = n(68),
      i = n(55),
      a = n(153),
      s = n(184),
      u = TypeError;
    e.exports = function (e, t) {
      var n = arguments.length < 2 ? s(e) : t;
      if (o(n)) return i(r(n, e));
      throw new u(a(e) + " is not iterable");
    };
  },
  232: function (e, t, n) {
    "use strict";
    var r = TypeError;
    e.exports = function (e, t) {
      if (e < t) throw new r("Not enough arguments");
      return e;
    };
  },
  245: function (e, t, n) {
    "use strict";
    var r = n(45),
      o = n(23),
      i = n(84),
      a = n(251),
      s = n(492),
      u = a("IE_PROTO"),
      c = Object,
      l = c.prototype;
    e.exports = s
      ? c.getPrototypeOf
      : function (e) {
          var t = i(e);
          if (r(t, u)) return t[u];
          var n = t.constructor;
          return o(n) && t instanceof n ? n.prototype : t instanceof c ? l : null;
        };
  },
  247: function (e, t, n) {
    "use strict";
    var r = n(176),
      o = n(22),
      i = n(20).String;
    e.exports =
      !!Object.getOwnPropertySymbols &&
      !o(function () {
        var e = Symbol("symbol detection");
        return !i(e) || !(Object(e) instanceof Symbol) || (!Symbol.sham && r && r < 41);
      });
  },
  248: function (e, t, n) {
    "use strict";
    var r = n(249);
    e.exports = function (e, t) {
      return r[e] || (r[e] = t || {});
    };
  },
  249: function (e, t, n) {
    "use strict";
    var r = n(92),
      o = n(20),
      i = n(250),
      a = "__core-js_shared__",
      s = (e.exports = o[a] || i(a, {}));
    (s.versions || (s.versions = [])).push({
      version: "3.36.1",
      mode: r ? "pure" : "global",
      copyright: "© 2014-2024 Denis Pushkarev (zloirock.ru)",
      license: "https://github.com/zloirock/core-js/blob/v3.36.1/LICENSE",
      source: "https://github.com/zloirock/core-js",
    });
  },
  250: function (e, t, n) {
    "use strict";
    var r = n(20),
      o = Object.defineProperty;
    e.exports = function (e, t) {
      try {
        o(r, e, {value: t, configurable: !0, writable: !0});
      } catch (n) {
        r[e] = t;
      }
      return t;
    };
  },
  251: function (e, t, n) {
    "use strict";
    var r = n(248),
      o = n(292),
      i = r("keys");
    e.exports = function (e) {
      return i[e] || (i[e] = o(e));
    };
  },
  252: function (e, t, n) {
    "use strict";
    e.exports = {};
  },
  253: function (e, t, n) {
    "use strict";
    e.exports = [
      "constructor",
      "hasOwnProperty",
      "isPrototypeOf",
      "propertyIsEnumerable",
      "toLocaleString",
      "toString",
      "valueOf",
    ];
  },
  254: function (e, t, n) {
    "use strict";
    var r,
      o,
      i = n(28),
      a = n(21),
      s = n(80),
      u = n(318),
      c = n(319),
      l = n(248),
      d = n(123),
      f = n(81).get,
      p = n(255),
      v = n(326),
      _ = l("native-string-replace", String.prototype.replace),
      y = RegExp.prototype.exec,
      h = y,
      g = a("".charAt),
      b = a("".indexOf),
      E = a("".replace),
      m = a("".slice),
      w =
        ((o = /b*/g),
        i(y, (r = /a/), "a"),
        i(y, o, "a"),
        0 !== r.lastIndex || 0 !== o.lastIndex),
      O = c.BROKEN_CARET,
      S = void 0 !== /()??/.exec("")[1];
    (w || S || O || p || v) &&
      (h = function exec(e) {
        var t,
          n,
          r,
          o,
          a,
          c,
          l,
          p = this,
          v = f(p),
          I = s(e),
          P = v.raw;
        if (P)
          return (
            (P.lastIndex = p.lastIndex),
            (t = i(h, P, I)),
            (p.lastIndex = P.lastIndex),
            t
          );
        var T = v.groups,
          L = O && p.sticky,
          x = i(u, p),
          A = p.source,
          N = 0,
          R = I;
        if (
          (L &&
            ((x = E(x, "y", "")),
            -1 === b(x, "g") && (x += "g"),
            (R = m(I, p.lastIndex)),
            p.lastIndex > 0 &&
              (!p.multiline || (p.multiline && "\n" !== g(I, p.lastIndex - 1))) &&
              ((A = "(?: " + A + ")"), (R = " " + R), N++),
            (n = new RegExp("^(?:" + A + ")", x))),
          S && (n = new RegExp("^" + A + "$(?!\\s)", x)),
          w && (r = p.lastIndex),
          (o = i(y, L ? n : p, R)),
          L
            ? o
              ? ((o.input = m(o.input, N)),
                (o[0] = m(o[0], N)),
                (o.index = p.lastIndex),
                (p.lastIndex += o[0].length))
              : (p.lastIndex = 0)
            : w && o && (p.lastIndex = p.global ? o.index + o[0].length : r),
          S &&
            o &&
            o.length > 1 &&
            i(_, o[0], n, function () {
              for (a = 1; a < arguments.length - 2; a++)
                void 0 === arguments[a] && (o[a] = void 0);
            }),
          o && T)
        )
          for (o.groups = c = d(null), a = 0; a < T.length; a++)
            c[(l = T[a])[0]] = o[l[1]];
        return o;
      }),
      (e.exports = h);
  },
  255: function (e, t, n) {
    "use strict";
    var r = n(22),
      o = n(20).RegExp;
    e.exports = r(function () {
      var e = o(".", "s");
      return !(e.dotAll && e.test("\n") && "s" === e.flags);
    });
  },
  264: function (e, t, n) {
    "use strict";
    var r = n(4);
    Object.defineProperty(t, "__esModule", {value: !0}), (t.default = void 0), n(13);
    var o = r(n(525));
    t.default = () => {
      if (null == window.navigator)
        return {
          browserLanguage: "",
          isAndroid: !1,
          isIE: !1,
          isIOS: !1,
          isIOSChrome: !1,
          isMobile: !1,
          isMac: !1,
          isWindows: !1,
          isLinux: !1,
        };
      const e = window.navigator,
        t = (() => {
          if (null != e.language && "" !== e.language) return e.language;
          const t = e.userLanguage;
          return null != t ? t : "";
        })(),
        n = /windows phone/i.test(e.userAgent),
        r = /android|silk/i.test(e.userAgent) && !n,
        i = /MSIE |Trident/i.test(e.userAgent),
        a = /iPad|iPhone|iPod/.test(e.userAgent) && !window.MSStream && !n,
        s = -1 !== e.platform.indexOf("Win"),
        u = -1 !== e.platform.indexOf("Mac"),
        c = -1 !== e.platform.indexOf("Linux"),
        l = a && !/Safari/i.test(e.userAgent);
      return {
        browserLanguage: t,
        isAndroid: r,
        isIE: i,
        isIOS: a,
        isIOSChrome: (0, o.default)().isIOSChrome,
        isMobile: (0, o.default)().isMobile,
        isWindows: s,
        isMac: u,
        isLinux: c,
        isIOSEmbeddedWebview: l,
      };
    };
  },
  265: function (e, t, n) {
    "use strict";
    var r = n(22),
      o = n(23),
      i = /#|\.prototype\./,
      isForced = function (e, t) {
        var n = s[a(e)];
        return n === c || (n !== u && (o(t) ? r(t) : !!t));
      },
      a = (isForced.normalize = function (e) {
        return String(e).replace(i, ".").toLowerCase();
      }),
      s = (isForced.data = {}),
      u = (isForced.NATIVE = "N"),
      c = (isForced.POLYFILL = "P");
    e.exports = isForced;
  },
  266: function (e, t, n) {
    "use strict";
    e.exports = function (e, t) {
      return {value: e, done: t};
    };
  },
  267: function (e, t, n) {
    "use strict";
    var r = n(188),
      o = Function.prototype,
      i = o.apply,
      a = o.call;
    e.exports =
      ("object" == typeof Reflect && Reflect.apply) ||
      (r
        ? a.bind(i)
        : function () {
            return a.apply(i, arguments);
          });
  },
  269: function (e, t, n) {
    "use strict";
    var r = n(21),
      o = n(23),
      i = n(249),
      a = r(Function.toString);
    o(i.inspectSource) ||
      (i.inspectSource = function (e) {
        return a(e);
      }),
      (e.exports = i.inspectSource);
  },
  27: function (e, t, n) {
    "use strict";
    var r = n(20),
      o = n(248),
      i = n(45),
      a = n(292),
      s = n(247),
      u = n(321),
      c = r.Symbol,
      l = o("wks"),
      d = u ? c.for || c : (c && c.withoutSetter) || a;
    e.exports = function (e) {
      return i(l, e) || (l[e] = s && i(c, e) ? c[e] : d("Symbol." + e)), l[e];
    };
  },
  270: function (e, t, n) {
    "use strict";
    var r = n(21),
      o = n(131),
      i = n(80),
      a = n(149),
      s = r("".charAt),
      u = r("".charCodeAt),
      c = r("".slice),
      createMethod = function (e) {
        return function (t, n) {
          var r,
            l,
            d = i(a(t)),
            f = o(n),
            p = d.length;
          return f < 0 || f >= p
            ? e
              ? ""
              : void 0
            : (r = u(d, f)) < 55296 ||
                r > 56319 ||
                f + 1 === p ||
                (l = u(d, f + 1)) < 56320 ||
                l > 57343
              ? e
                ? s(d, f)
                : r
              : e
                ? c(d, f, f + 2)
                : l - 56320 + ((r - 55296) << 10) + 65536;
        };
      };
    e.exports = {codeAt: createMethod(!1), charAt: createMethod(!0)};
  },
  271: function (e, t, n) {
    "use strict";
    var r = n(27),
      o = n(123),
      i = n(78).f,
      a = r("unscopables"),
      s = Array.prototype;
    void 0 === s[a] && i(s, a, {configurable: !0, value: o(null)}),
      (e.exports = function (e) {
        s[a][e] = !0;
      });
  },
  274: function (e, t, n) {
    "use strict";
    var r = n(30),
      o = n(45),
      i = Function.prototype,
      a = r && Object.getOwnPropertyDescriptor,
      s = o(i, "name"),
      u = s && "something" === function something() {}.name,
      c = s && (!r || (r && a(i, "name").configurable));
    e.exports = {EXISTS: s, PROPER: u, CONFIGURABLE: c};
  },
  279: function (e, t, n) {
    "use strict";
    Object.defineProperty(t, "__esModule", {value: !0}),
      (t.Web3MessageToTopWindow = t.Web3MessageToIFrame = t.PostMessageAction = void 0);
    let r = (function (e) {
      return (
        (e.Acknowledged = "acknowledged"),
        (e.Connected = "connected"),
        (e.Event = "event"),
        (e.Exit = "exit"),
        (e.InternalEvent = "internal-event"),
        (e.Ready = "ready"),
        (e.ReadyForConfigure = "ready-for-configure"),
        (e.Resize = "resize"),
        (e.Result = "result"),
        (e.TrackingReady = "tracking-ready"),
        (e.Web3Message = "web3-message"),
        (e.EmbeddedLinkLoaded = "embedded-link-loaded"),
        (e.EmbeddedSesionHandoff = "embedded-session-handoff"),
        (e.PreopenPopupWindow = "preopen-popup-window"),
        (e.EmbeddedLinkResize = "embedded-link-resize"),
        e
      );
    })({});
    t.PostMessageAction = r;
    let o = (function (e) {
      return (
        (e.PROVIDER_CONNECTED = "PROVIDER_CONNECTED"),
        (e.PROVIDER_ERROR = "PROVIDER_ERROR"),
        (e.PROVIDER_CHAIN_INCORRECT = "PROVIDER_CHAIN_INCORRECT"),
        (e.PROVIDER_CHAIN_ADD_REQUIRED = "PROVIDER_CHAIN_ADD_REQUIRED"),
        (e.PROVIDER_MANUAL_CHAIN_REQUIRED = "PROVIDER_MANUAL_CHAIN_REQUIRED"),
        (e.RESPONSE_WALLETCONNECT_V1_URI = "RESPONSE_WALLETCONNECT_V1_URI"),
        (e.RESPONSE_WALLETCONNECT_V2_URI = "RESPONSE_WALLETCONNECT_V2_URI"),
        (e.RESPONSE_COINBASE_WALLET_DATA = "RESPONSE_COINBASE_WALLET_DATA"),
        (e.RESPONSE_PLUGIN_DATA = "RESPONSE_PLUGIN_DATA"),
        (e.RESPONSE_WALLET_SIGNATURE = "RESPONSE_WALLET_SIGNATURE"),
        e
      );
    })({});
    t.Web3MessageToIFrame = o;
    let i = (function (e) {
      return (
        (e.OPEN_BROWSER_PLUGIN = "OPEN_BROWSER_PLUGIN"),
        (e.OPEN_URI = "OPEN_URI"),
        (e.REQUEST_WALLETCONNECT_V1_URI = "REQUEST_WALLETCONNECT_V1_URI"),
        (e.REQUEST_WALLETCONNECT_V2_URI = "REQUEST_WALLETCONNECT_V2_URI"),
        (e.REQUEST_COINBASE_WALLET_DATA = "REQUEST_COINBASE_WALLET_DATA"),
        (e.REQUEST_PLUGIN_DATA = "REQUEST_PLUGIN_DATA"),
        (e.REQUEST_CHAIN_SWITCH = "REQUEST_CHAIN_SWITCH"),
        (e.REQUEST_CHAIN_ADD = "REQUEST_CHAIN_ADD"),
        (e.REQUEST_WALLET_SIGNATURE = "REQUEST_WALLET_SIGNATURE"),
        (e.COPY_TO_CLIPBOARD = "COPY_TO_CLIPBOARD"),
        (e.START_BRIDGE = "START_BRIDGE"),
        e
      );
    })({});
    t.Web3MessageToTopWindow = i;
  },
  2792: function (e, t) {
    (e.exports = function _interopRequireDefault(e) {
      return e && e.__esModule ? e : {default: e};
    }),
      (e.exports.__esModule = !0),
      (e.exports.default = e.exports);
  },
  2793: function (e, t) {
    var n = (e.exports =
      "undefined" != typeof window && window.Math == Math
        ? window
        : "undefined" != typeof self && self.Math == Math
          ? self
          : Function("return this")());
    "number" == typeof __g && (__g = n);
  },
  2794: function (e, t) {
    var n = (e.exports = {version: "2.6.12"});
    "number" == typeof __e && (__e = n);
  },
  28: function (e, t, n) {
    "use strict";
    var r = n(188),
      o = Function.prototype.call;
    e.exports = r
      ? o.bind(o)
      : function () {
          return o.apply(o, arguments);
        };
  },
  2877: function (e, t, n) {
    var r = n(3471),
      o = n(4306),
      i = n(3530),
      a = Object.defineProperty;
    t.f = n(2878)
      ? Object.defineProperty
      : function defineProperty(e, t, n) {
          if ((r(e), (t = i(t, !0)), r(n), o))
            try {
              return a(e, t, n);
            } catch (e) {}
          if ("get" in n || "set" in n) throw TypeError("Accessors not supported!");
          return "value" in n && (e[t] = n.value), e;
        };
  },
  2878: function (e, t, n) {
    e.exports = !n(3099)(function () {
      return (
        7 !=
        Object.defineProperty({}, "a", {
          get: function () {
            return 7;
          },
        }).a
      );
    });
  },
  2879: function (e, t) {
    var n = {}.hasOwnProperty;
    e.exports = function (e, t) {
      return n.call(e, t);
    };
  },
  29: function (e, t, n) {
    "use strict";
    var r = n(20),
      o = n(290).f,
      i = n(107),
      a = n(76),
      s = n(250),
      u = n(296),
      c = n(265);
    e.exports = function (e, t) {
      var n,
        l,
        d,
        f,
        p,
        v = e.target,
        _ = e.global,
        y = e.stat;
      if ((n = _ ? r : y ? r[v] || s(v, {}) : r[v] && r[v].prototype))
        for (l in t) {
          if (
            ((f = t[l]),
            (d = e.dontCallGetSet ? (p = o(n, l)) && p.value : n[l]),
            !c(_ ? l : v + (y ? "." : "#") + l, e.forced) && void 0 !== d)
          ) {
            if (typeof f == typeof d) continue;
            u(f, d);
          }
          (e.sham || (d && d.sham)) && i(f, "sham", !0), a(n, l, f, e);
        }
    };
  },
  290: function (e, t, n) {
    "use strict";
    var r = n(30),
      o = n(28),
      i = n(341),
      a = n(141),
      s = n(157),
      u = n(291),
      c = n(45),
      l = n(322),
      d = Object.getOwnPropertyDescriptor;
    t.f = r
      ? d
      : function getOwnPropertyDescriptor(e, t) {
          if (((e = s(e)), (t = u(t)), l))
            try {
              return d(e, t);
            } catch (e) {}
          if (c(e, t)) return a(!o(i.f, e, t), e[t]);
        };
  },
  291: function (e, t, n) {
    "use strict";
    var r = n(405),
      o = n(216);
    e.exports = function (e) {
      var t = r(e, "string");
      return o(t) ? t : t + "";
    };
  },
  292: function (e, t, n) {
    "use strict";
    var r = n(21),
      o = 0,
      i = Math.random(),
      a = r((1).toString);
    e.exports = function (e) {
      return "Symbol(" + (void 0 === e ? "" : e) + ")_" + a(++o + i, 36);
    };
  },
  293: function (e, t, n) {
    "use strict";
    var r = n(325),
      o = n(253).concat("length", "prototype");
    t.f =
      Object.getOwnPropertyNames ||
      function getOwnPropertyNames(e) {
        return r(e, o);
      };
  },
  296: function (e, t, n) {
    "use strict";
    var r = n(45),
      o = n(487),
      i = n(290),
      a = n(78);
    e.exports = function (e, t, n) {
      for (var s = o(t), u = a.f, c = i.f, l = 0; l < s.length; l++) {
        var d = s[l];
        r(e, d) || (n && r(n, d)) || u(e, d, c(t, d));
      }
    };
  },
  297: function (e, t, n) {
    "use strict";
    var r = n(101),
      o = n(135),
      i = n(27),
      a = n(30),
      s = i("species");
    e.exports = function (e) {
      var t = r(e);
      a &&
        t &&
        !t[s] &&
        o(t, s, {
          configurable: !0,
          get: function () {
            return this;
          },
        });
    };
  },
  298: function (e, t, n) {
    "use strict";
    var r = n(185),
      o = Math.floor,
      sort = function (e, t) {
        var n = e.length;
        if (n < 8)
          for (var i, a, s = 1; s < n; ) {
            for (a = s, i = e[s]; a && t(e[a - 1], i) > 0; ) e[a] = e[--a];
            a !== s++ && (e[a] = i);
          }
        else
          for (
            var u = o(n / 2),
              c = sort(r(e, 0, u), t),
              l = sort(r(e, u), t),
              d = c.length,
              f = l.length,
              p = 0,
              v = 0;
            p < d || v < f;

          )
            e[p + v] =
              p < d && v < f
                ? t(c[p], l[v]) <= 0
                  ? c[p++]
                  : l[v++]
                : p < d
                  ? c[p++]
                  : l[v++];
        return e;
      };
    e.exports = sort;
  },
  3: function (e, t, n) {
    "use strict";
    var r = n(20),
      o = n(496),
      i = n(497),
      a = n(2),
      s = n(107),
      u = n(122),
      c = n(27)("iterator"),
      l = a.values,
      handlePrototype = function (e, t) {
        if (e) {
          if (e[c] !== l)
            try {
              s(e, c, l);
            } catch (t) {
              e[c] = l;
            }
          if ((u(e, t, !0), o[t]))
            for (var n in a)
              if (e[n] !== a[n])
                try {
                  s(e, n, a[n]);
                } catch (t) {
                  e[n] = a[n];
                }
        }
      };
    for (var d in o) handlePrototype(r[d] && r[d].prototype, d);
    handlePrototype(i, "DOMTokenList");
  },
  30: function (e, t, n) {
    "use strict";
    var r = n(22);
    e.exports = !r(function () {
      return (
        7 !==
        Object.defineProperty({}, 1, {
          get: function () {
            return 7;
          },
        })[1]
      );
    });
  },
  306: function (e, t, n) {
    "use strict";
    Object.defineProperty(t, "__esModule", {value: !0}),
      (t.default = void 0),
      n(13),
      n(37);
    var _default = () => {
      const e = window.crypto || window.msCrypto;
      return null != e && "randomUUID" in e
        ? e.randomUUID()
        : "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (e) {
            const t = (16 * Math.random()) | 0;
            return ("x" === e ? t : (3 & t) | 8).toString(16);
          });
    };
    t.default = _default;
  },
  3073: function (e, t, n) {
    var r = n(4429),
      o = n(4434);
    (e.exports = function _defineProperty(e, t, n) {
      return (
        (t = o(t)) in e
          ? r(e, t, {value: n, enumerable: !0, configurable: !0, writable: !0})
          : (e[t] = n),
        e
      );
    }),
      (e.exports.__esModule = !0),
      (e.exports.default = e.exports);
  },
  3074: function (e, t, n) {
    var r = n(2877),
      o = n(3472);
    e.exports = n(2878)
      ? function (e, t, n) {
          return r.f(e, t, o(1, n));
        }
      : function (e, t, n) {
          return (e[t] = n), e;
        };
  },
  3075: function (e, t, n) {
    var r = n(3531)("wks"),
      o = n(3473),
      i = n(2793).Symbol,
      a = "function" == typeof i;
    (e.exports = function (e) {
      return r[e] || (r[e] = (a && i[e]) || (a ? i : o)("Symbol." + e));
    }).store = r;
  },
  3076: function (e, t, n) {
    var r = n(4439),
      o = n(3529);
    e.exports = function (e) {
      return r(o(e));
    };
  },
  3099: function (e, t) {
    e.exports = function (e) {
      try {
        return !!e();
      } catch (e) {
        return !0;
      }
    };
  },
  3100: function (e, t) {
    e.exports = function (e) {
      return "object" == typeof e ? null !== e : "function" == typeof e;
    };
  },
  316: function (e, t, n) {
    "use strict";
    var r = n(22);
    e.exports = function (e, t) {
      var n = [][e];
      return (
        !!n &&
        r(function () {
          n.call(
            null,
            t ||
              function () {
                return 1;
              },
            1
          );
        })
      );
    };
  },
  318: function (e, t, n) {
    "use strict";
    var r = n(55);
    e.exports = function () {
      var e = r(this),
        t = "";
      return (
        e.hasIndices && (t += "d"),
        e.global && (t += "g"),
        e.ignoreCase && (t += "i"),
        e.multiline && (t += "m"),
        e.dotAll && (t += "s"),
        e.unicode && (t += "u"),
        e.unicodeSets && (t += "v"),
        e.sticky && (t += "y"),
        t
      );
    };
  },
  319: function (e, t, n) {
    "use strict";
    var r = n(22),
      o = n(20).RegExp,
      i = r(function () {
        var e = o("a", "y");
        return (e.lastIndex = 2), null !== e.exec("abcd");
      }),
      a =
        i ||
        r(function () {
          return !o("a", "y").sticky;
        }),
      s =
        i ||
        r(function () {
          var e = o("^r", "gy");
          return (e.lastIndex = 2), null !== e.exec("str");
        });
    e.exports = {BROKEN_CARET: s, MISSED_STICKY: a, UNSUPPORTED_Y: i};
  },
  320: function (e, t, n) {
    "use strict";
    var r = n(90);
    e.exports =
      Array.isArray ||
      function isArray(e) {
        return "Array" === r(e);
      };
  },
  321: function (e, t, n) {
    "use strict";
    var r = n(247);
    e.exports = r && !Symbol.sham && "symbol" == typeof Symbol.iterator;
  },
  322: function (e, t, n) {
    "use strict";
    var r = n(30),
      o = n(22),
      i = n(198);
    e.exports =
      !r &&
      !o(function () {
        return (
          7 !==
          Object.defineProperty(i("div"), "a", {
            get: function () {
              return 7;
            },
          }).a
        );
      });
  },
  323: function (e, t, n) {
    "use strict";
    var r = n(30),
      o = n(22);
    e.exports =
      r &&
      o(function () {
        return (
          42 !==
          Object.defineProperty(function () {}, "prototype", {value: 42, writable: !1})
            .prototype
        );
      });
  },
  324: function (e, t, n) {
    "use strict";
    var r = n(21),
      o = n(22),
      i = n(23),
      a = n(45),
      s = n(30),
      u = n(274).CONFIGURABLE,
      c = n(269),
      l = n(81),
      d = l.enforce,
      f = l.get,
      p = String,
      v = Object.defineProperty,
      _ = r("".slice),
      y = r("".replace),
      h = r([].join),
      g =
        s &&
        !o(function () {
          return 8 !== v(function () {}, "length", {value: 8}).length;
        }),
      b = String(String).split("String"),
      E = (e.exports = function (e, t, n) {
        "Symbol(" === _(p(t), 0, 7) &&
          (t = "[" + y(p(t), /^Symbol\(([^)]*)\).*$/, "$1") + "]"),
          n && n.getter && (t = "get " + t),
          n && n.setter && (t = "set " + t),
          (!a(e, "name") || (u && e.name !== t)) &&
            (s ? v(e, "name", {value: t, configurable: !0}) : (e.name = t)),
          g &&
            n &&
            a(n, "arity") &&
            e.length !== n.arity &&
            v(e, "length", {value: n.arity});
        try {
          n && a(n, "constructor") && n.constructor
            ? s && v(e, "prototype", {writable: !1})
            : e.prototype && (e.prototype = void 0);
        } catch (e) {}
        var r = d(e);
        return a(r, "source") || (r.source = h(b, "string" == typeof t ? t : "")), e;
      });
    Function.prototype.toString = E(function toString() {
      return (i(this) && f(this).source) || c(this);
    }, "toString");
  },
  325: function (e, t, n) {
    "use strict";
    var r = n(21),
      o = n(45),
      i = n(157),
      a = n(342).indexOf,
      s = n(252),
      u = r([].push);
    e.exports = function (e, t) {
      var n,
        r = i(e),
        c = 0,
        l = [];
      for (n in r) !o(s, n) && o(r, n) && u(l, n);
      for (; t.length > c; ) o(r, (n = t[c++])) && (~a(l, n) || u(l, n));
      return l;
    };
  },
  326: function (e, t, n) {
    "use strict";
    var r = n(22),
      o = n(20).RegExp;
    e.exports = r(function () {
      var e = o("(?<a>b)", "g");
      return "b" !== e.exec("b").groups.a || "bc" !== "b".replace(e, "$<a>c");
    });
  },
  327: function (e, t) {
    function _typeof(t) {
      return (
        (e.exports = _typeof =
          "function" == typeof Symbol && "symbol" == typeof Symbol.iterator
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
        (e.exports.__esModule = !0),
        (e.exports.default = e.exports),
        _typeof(t)
      );
    }
    (e.exports = _typeof), (e.exports.__esModule = !0), (e.exports.default = e.exports);
  },
  328: function (e, t, n) {
    "use strict";
    var r = n(329).IteratorPrototype,
      o = n(123),
      i = n(141),
      a = n(122),
      s = n(160),
      returnThis = function () {
        return this;
      };
    e.exports = function (e, t, n, u) {
      var c = t + " Iterator";
      return (
        (e.prototype = o(r, {next: i(+!u, n)})), a(e, c, !1, !0), (s[c] = returnThis), e
      );
    };
  },
  329: function (e, t, n) {
    "use strict";
    var r,
      o,
      i,
      a = n(22),
      s = n(23),
      u = n(51),
      c = n(123),
      l = n(245),
      d = n(76),
      f = n(27),
      p = n(92),
      v = f("iterator"),
      _ = !1;
    [].keys &&
      ("next" in (i = [].keys())
        ? (o = l(l(i))) !== Object.prototype && (r = o)
        : (_ = !0)),
      !u(r) ||
      a(function () {
        var e = {};
        return r[v].call(e) !== e;
      })
        ? (r = {})
        : p && (r = c(r)),
      s(r[v]) ||
        d(r, v, function () {
          return this;
        }),
      (e.exports = {IteratorPrototype: r, BUGGY_SAFARI_ITERATORS: _});
  },
  339: function (e, t, n) {
    "use strict";
    var r = n(325),
      o = n(253);
    e.exports =
      Object.keys ||
      function keys(e) {
        return r(e, o);
      };
  },
  341: function (e, t, n) {
    "use strict";
    var r = {}.propertyIsEnumerable,
      o = Object.getOwnPropertyDescriptor,
      i = o && !r.call({1: 2}, 1);
    t.f = i
      ? function propertyIsEnumerable(e) {
          var t = o(this, e);
          return !!t && t.enumerable;
        }
      : r;
  },
  342: function (e, t, n) {
    "use strict";
    var r = n(157),
      o = n(406),
      i = n(89),
      createMethod = function (e) {
        return function (t, n, a) {
          var s = r(t),
            u = i(s);
          if (0 === u) return !e && -1;
          var c,
            l = o(a, u);
          if (e && n != n) {
            for (; u > l; ) if ((c = s[l++]) != c) return !0;
          } else for (; u > l; l++) if ((e || l in s) && s[l] === n) return e || l || 0;
          return !e && -1;
        };
      };
    e.exports = {includes: createMethod(!0), indexOf: createMethod(!1)};
  },
  343: function (e, t, n) {
    "use strict";
    t.f = Object.getOwnPropertySymbols;
  },
  344: function (e, t, n) {
    "use strict";
    var r = n(101);
    e.exports = r("document", "documentElement");
  },
  345: function (e, t, n) {
    "use strict";
    var r = n(29),
      o = n(28),
      i = n(92),
      a = n(274),
      s = n(23),
      u = n(328),
      c = n(245),
      l = n(178),
      d = n(122),
      f = n(107),
      p = n(76),
      v = n(27),
      _ = n(160),
      y = n(329),
      h = a.PROPER,
      g = a.CONFIGURABLE,
      b = y.IteratorPrototype,
      E = y.BUGGY_SAFARI_ITERATORS,
      m = v("iterator"),
      w = "keys",
      O = "values",
      S = "entries",
      returnThis = function () {
        return this;
      };
    e.exports = function (e, t, n, a, v, y, I) {
      u(n, t, a);
      var P,
        T,
        L,
        getIterationMethod = function (e) {
          if (e === v && k) return k;
          if (!E && e && e in N) return N[e];
          switch (e) {
            case w:
              return function keys() {
                return new n(this, e);
              };
            case O:
              return function values() {
                return new n(this, e);
              };
            case S:
              return function entries() {
                return new n(this, e);
              };
          }
          return function () {
            return new n(this);
          };
        },
        x = t + " Iterator",
        A = !1,
        N = e.prototype,
        R = N[m] || N["@@iterator"] || (v && N[v]),
        k = (!E && R) || getIterationMethod(v),
        C = ("Array" === t && N.entries) || R;
      if (
        (C &&
          (P = c(C.call(new e()))) !== Object.prototype &&
          P.next &&
          (i || c(P) === b || (l ? l(P, b) : s(P[m]) || p(P, m, returnThis)),
          d(P, x, !0, !0),
          i && (_[x] = returnThis)),
        h &&
          v === O &&
          R &&
          R.name !== O &&
          (!i && g
            ? f(N, "name", O)
            : ((A = !0),
              (k = function values() {
                return o(R, this);
              }))),
        v)
      )
        if (
          ((T = {
            values: getIterationMethod(O),
            keys: y ? k : getIterationMethod(w),
            entries: getIterationMethod(S),
          }),
          I)
        )
          for (L in T) (E || A || !(L in N)) && p(N, L, T[L]);
        else r({target: t, proto: !0, forced: E || A}, T);
      return (i && !I) || N[m] === k || p(N, m, k, {name: v}), (_[t] = k), T;
    };
  },
  346: function (e, t, n) {
    "use strict";
    n(2);
    var r = n(29),
      o = n(20),
      i = n(347),
      a = n(28),
      s = n(21),
      u = n(30),
      c = n(348),
      l = n(76),
      d = n(135),
      f = n(407),
      p = n(122),
      v = n(328),
      _ = n(81),
      y = n(207),
      h = n(23),
      g = n(45),
      b = n(113),
      E = n(139),
      m = n(55),
      w = n(51),
      O = n(80),
      S = n(123),
      I = n(141),
      P = n(231),
      T = n(184),
      L = n(266),
      x = n(232),
      A = n(27),
      N = n(298),
      R = A("iterator"),
      k = "URLSearchParams",
      C = "URLSearchParamsIterator",
      M = _.set,
      j = _.getterFor(k),
      D = _.getterFor(C),
      U = i("fetch"),
      W = i("Request"),
      V = i("Headers"),
      K = W && W.prototype,
      H = V && V.prototype,
      B = o.RegExp,
      q = o.TypeError,
      G = o.decodeURIComponent,
      z = o.encodeURIComponent,
      $ = s("".charAt),
      Q = s([].join),
      X = s([].push),
      Y = s("".replace),
      J = s([].shift),
      Z = s([].splice),
      ee = s("".split),
      te = s("".slice),
      ne = /\+/g,
      re = Array(4),
      percentSequence = function (e) {
        return re[e - 1] || (re[e - 1] = B("((?:%[\\da-f]{2}){" + e + "})", "gi"));
      },
      percentDecode = function (e) {
        try {
          return G(e);
        } catch (t) {
          return e;
        }
      },
      deserialize = function (e) {
        var t = Y(e, ne, " "),
          n = 4;
        try {
          return G(t);
        } catch (e) {
          for (; n; ) t = Y(t, percentSequence(n--), percentDecode);
          return t;
        }
      },
      oe = /[!'()~]|%20/g,
      ie = {"!": "%21", "'": "%27", "(": "%28", ")": "%29", "~": "%7E", "%20": "+"},
      replacer = function (e) {
        return ie[e];
      },
      serialize = function (e) {
        return Y(z(e), oe, replacer);
      },
      ae = v(
        function Iterator(e, t) {
          M(this, {type: C, target: j(e).entries, index: 0, kind: t});
        },
        k,
        function next() {
          var e = D(this),
            t = e.target,
            n = e.index++;
          if (!t || n >= t.length) return (e.target = void 0), L(void 0, !0);
          var r = t[n];
          switch (e.kind) {
            case "keys":
              return L(r.key, !1);
            case "values":
              return L(r.value, !1);
          }
          return L([r.key, r.value], !1);
        },
        !0
      ),
      URLSearchParamsState = function (e) {
        (this.entries = []),
          (this.url = null),
          void 0 !== e &&
            (w(e)
              ? this.parseObject(e)
              : this.parseQuery(
                  "string" == typeof e ? ("?" === $(e, 0) ? te(e, 1) : e) : O(e)
                ));
      };
    URLSearchParamsState.prototype = {
      type: k,
      bindURL: function (e) {
        (this.url = e), this.update();
      },
      parseObject: function (e) {
        var t,
          n,
          r,
          o,
          i,
          s,
          u,
          c = this.entries,
          l = T(e);
        if (l)
          for (n = (t = P(e, l)).next; !(r = a(n, t)).done; ) {
            if (
              ((i = (o = P(m(r.value))).next),
              (s = a(i, o)).done || (u = a(i, o)).done || !a(i, o).done)
            )
              throw new q("Expected sequence with length 2");
            X(c, {key: O(s.value), value: O(u.value)});
          }
        else for (var d in e) g(e, d) && X(c, {key: d, value: O(e[d])});
      },
      parseQuery: function (e) {
        if (e)
          for (var t, n, r = this.entries, o = ee(e, "&"), i = 0; i < o.length; )
            (t = o[i++]).length &&
              ((n = ee(t, "=")),
              X(r, {key: deserialize(J(n)), value: deserialize(Q(n, "="))}));
      },
      serialize: function () {
        for (var e, t = this.entries, n = [], r = 0; r < t.length; )
          (e = t[r++]), X(n, serialize(e.key) + "=" + serialize(e.value));
        return Q(n, "&");
      },
      update: function () {
        (this.entries.length = 0), this.parseQuery(this.url.query);
      },
      updateURL: function () {
        this.url && this.url.update();
      },
    };
    var se = function URLSearchParams() {
        y(this, ue);
        var e = arguments.length > 0 ? arguments[0] : void 0,
          t = M(this, new URLSearchParamsState(e));
        u || (this.size = t.entries.length);
      },
      ue = se.prototype;
    if (
      (f(
        ue,
        {
          append: function append(e, t) {
            var n = j(this);
            x(arguments.length, 2),
              X(n.entries, {key: O(e), value: O(t)}),
              u || this.length++,
              n.updateURL();
          },
          delete: function (e) {
            for (
              var t = j(this),
                n = x(arguments.length, 1),
                r = t.entries,
                o = O(e),
                i = n < 2 ? void 0 : arguments[1],
                a = void 0 === i ? i : O(i),
                s = 0;
              s < r.length;

            ) {
              var c = r[s];
              if (c.key !== o || (void 0 !== a && c.value !== a)) s++;
              else if ((Z(r, s, 1), void 0 !== a)) break;
            }
            u || (this.size = r.length), t.updateURL();
          },
          get: function get(e) {
            var t = j(this).entries;
            x(arguments.length, 1);
            for (var n = O(e), r = 0; r < t.length; r++)
              if (t[r].key === n) return t[r].value;
            return null;
          },
          getAll: function getAll(e) {
            var t = j(this).entries;
            x(arguments.length, 1);
            for (var n = O(e), r = [], o = 0; o < t.length; o++)
              t[o].key === n && X(r, t[o].value);
            return r;
          },
          has: function has(e) {
            for (
              var t = j(this).entries,
                n = x(arguments.length, 1),
                r = O(e),
                o = n < 2 ? void 0 : arguments[1],
                i = void 0 === o ? o : O(o),
                a = 0;
              a < t.length;

            ) {
              var s = t[a++];
              if (s.key === r && (void 0 === i || s.value === i)) return !0;
            }
            return !1;
          },
          set: function set(e, t) {
            var n = j(this);
            x(arguments.length, 1);
            for (
              var r, o = n.entries, i = !1, a = O(e), s = O(t), c = 0;
              c < o.length;
              c++
            )
              (r = o[c]).key === a && (i ? Z(o, c--, 1) : ((i = !0), (r.value = s)));
            i || X(o, {key: a, value: s}), u || (this.size = o.length), n.updateURL();
          },
          sort: function sort() {
            var e = j(this);
            N(e.entries, function (e, t) {
              return e.key > t.key ? 1 : -1;
            }),
              e.updateURL();
          },
          forEach: function forEach(e) {
            for (
              var t,
                n = j(this).entries,
                r = b(e, arguments.length > 1 ? arguments[1] : void 0),
                o = 0;
              o < n.length;

            )
              r((t = n[o++]).value, t.key, this);
          },
          keys: function keys() {
            return new ae(this, "keys");
          },
          values: function values() {
            return new ae(this, "values");
          },
          entries: function entries() {
            return new ae(this, "entries");
          },
        },
        {enumerable: !0}
      ),
      l(ue, R, ue.entries, {name: "entries"}),
      l(
        ue,
        "toString",
        function toString() {
          return j(this).serialize();
        },
        {enumerable: !0}
      ),
      u &&
        d(ue, "size", {
          get: function size() {
            return j(this).entries.length;
          },
          configurable: !0,
          enumerable: !0,
        }),
      p(se, k),
      r({global: !0, constructor: !0, forced: !c}, {URLSearchParams: se}),
      !c && h(V))
    ) {
      var ce = s(H.has),
        le = s(H.set),
        wrapRequestOptions = function (e) {
          if (w(e)) {
            var t,
              n = e.body;
            if (E(n) === k)
              return (
                (t = e.headers ? new V(e.headers) : new V()),
                ce(t, "content-type") ||
                  le(
                    t,
                    "content-type",
                    "application/x-www-form-urlencoded;charset=UTF-8"
                  ),
                S(e, {body: I(0, O(n)), headers: I(0, t)})
              );
          }
          return e;
        };
      if (
        (h(U) &&
          r(
            {global: !0, enumerable: !0, dontCallGetSet: !0, forced: !0},
            {
              fetch: function fetch(e) {
                return U(
                  e,
                  arguments.length > 1 ? wrapRequestOptions(arguments[1]) : {}
                );
              },
            }
          ),
        h(W))
      ) {
        var de = function Request(e) {
          return (
            y(this, K),
            new W(e, arguments.length > 1 ? wrapRequestOptions(arguments[1]) : {})
          );
        };
        (K.constructor = de),
          (de.prototype = K),
          r(
            {global: !0, constructor: !0, dontCallGetSet: !0, forced: !0},
            {Request: de}
          );
      }
    }
    e.exports = {URLSearchParams: se, getState: j};
  },
  347: function (e, t, n) {
    "use strict";
    var r = n(20),
      o = n(30),
      i = Object.getOwnPropertyDescriptor;
    e.exports = function (e) {
      if (!o) return r[e];
      var t = i(r, e);
      return t && t.value;
    };
  },
  3470: function (e, t, n) {
    var r = n(2793),
      o = n(2794),
      i = n(4432),
      a = n(3074),
      s = n(2879),
      $export = function (e, t, n) {
        var u,
          c,
          l,
          d = e & $export.F,
          f = e & $export.G,
          p = e & $export.S,
          v = e & $export.P,
          _ = e & $export.B,
          y = e & $export.W,
          h = f ? o : o[t] || (o[t] = {}),
          g = h.prototype,
          b = f ? r : p ? r[t] : (r[t] || {}).prototype;
        for (u in (f && (n = t), n))
          ((c = !d && b && void 0 !== b[u]) && s(h, u)) ||
            ((l = c ? b[u] : n[u]),
            (h[u] =
              f && "function" != typeof b[u]
                ? n[u]
                : _ && c
                  ? i(l, r)
                  : y && b[u] == l
                    ? (function (e) {
                        var F = function (t, n, r) {
                          if (this instanceof e) {
                            switch (arguments.length) {
                              case 0:
                                return new e();
                              case 1:
                                return new e(t);
                              case 2:
                                return new e(t, n);
                            }
                            return new e(t, n, r);
                          }
                          return e.apply(this, arguments);
                        };
                        return (F.prototype = e.prototype), F;
                      })(l)
                    : v && "function" == typeof l
                      ? i(Function.call, l)
                      : l),
            v &&
              (((h.virtual || (h.virtual = {}))[u] = l),
              e & $export.R && g && !g[u] && a(g, u, l)));
      };
    ($export.F = 1),
      ($export.G = 2),
      ($export.S = 4),
      ($export.P = 8),
      ($export.B = 16),
      ($export.W = 32),
      ($export.U = 64),
      ($export.R = 128),
      (e.exports = $export);
  },
  3471: function (e, t, n) {
    var r = n(3100);
    e.exports = function (e) {
      if (!r(e)) throw TypeError(e + " is not an object!");
      return e;
    };
  },
  3472: function (e, t) {
    e.exports = function (e, t) {
      return {
        enumerable: !(1 & e),
        configurable: !(2 & e),
        writable: !(4 & e),
        value: t,
      };
    };
  },
  3473: function (e, t) {
    var n = 0,
      r = Math.random();
    e.exports = function (e) {
      return "Symbol(".concat(void 0 === e ? "" : e, ")_", (++n + r).toString(36));
    };
  },
  3474: function (e, t) {
    e.exports = !0;
  },
  3475: function (e, t, n) {
    t.f = n(3075);
  },
  3477: function (e, t, n) {
    var r = n(4310),
      o = n(3536);
    e.exports =
      Object.keys ||
      function keys(e) {
        return r(e, o);
      };
  },
  348: function (e, t, n) {
    "use strict";
    var r = n(22),
      o = n(27),
      i = n(30),
      a = n(92),
      s = o("iterator");
    e.exports = !r(function () {
      var e = new URL("b?a=1&b=2&c=3", "http://a"),
        t = e.searchParams,
        n = new URLSearchParams("a=1&a=2&b=3"),
        r = "";
      return (
        (e.pathname = "c%20d"),
        t.forEach(function (e, n) {
          t.delete("b"), (r += n + e);
        }),
        n.delete("a", 2),
        n.delete("b", void 0),
        (a &&
          (!e.toJSON ||
            !n.has("a", 1) ||
            n.has("a", 2) ||
            !n.has("a", void 0) ||
            n.has("b"))) ||
          (!t.size && (a || !i)) ||
          !t.sort ||
          "http://a/c%20d?a=1&c=3" !== e.href ||
          "3" !== t.get("c") ||
          "a=1" !== String(new URLSearchParams("?a=1")) ||
          !t[s] ||
          "a" !== new URL("https://a@b").username ||
          "b" !== new URLSearchParams(new URLSearchParams("a=b")).get("a") ||
          "xn--e1aybc" !== new URL("http://тест").host ||
          "#%D0%B1" !== new URL("http://a#б").hash ||
          "a1c3" !== r ||
          "x" !== new URL("http://x", void 0).host
      );
    });
  },
  351: function (e, t, n) {
    "use strict";
    var r = n(23),
      o = n(51),
      i = n(178);
    e.exports = function (e, t, n) {
      var a, s;
      return (
        i &&
          r((a = t.constructor)) &&
          a !== n &&
          o((s = a.prototype)) &&
          s !== n.prototype &&
          i(e, s),
        e
      );
    };
  },
  3529: function (e, t) {
    e.exports = function (e) {
      if (null == e) throw TypeError("Can't call method on  " + e);
      return e;
    };
  },
  3530: function (e, t, n) {
    var r = n(3100);
    e.exports = function (e, t) {
      if (!r(e)) return e;
      var n, o;
      if (t && "function" == typeof (n = e.toString) && !r((o = n.call(e)))) return o;
      if ("function" == typeof (n = e.valueOf) && !r((o = n.call(e)))) return o;
      if (!t && "function" == typeof (n = e.toString) && !r((o = n.call(e)))) return o;
      throw TypeError("Can't convert object to primitive value");
    };
  },
  3531: function (e, t, n) {
    var r = n(2794),
      o = n(2793),
      i = "__core-js_shared__",
      a = o[i] || (o[i] = {});
    (e.exports = function (e, t) {
      return a[e] || (a[e] = void 0 !== t ? t : {});
    })("versions", []).push({
      version: r.version,
      mode: n(3474) ? "pure" : "global",
      copyright: "© 2020 Denis Pushkarev (zloirock.ru)",
    });
  },
  3532: function (e, t, n) {
    var r = n(2877).f,
      o = n(2879),
      i = n(3075)("toStringTag");
    e.exports = function (e, t, n) {
      e && !o((e = n ? e : e.prototype), i) && r(e, i, {configurable: !0, value: t});
    };
  },
  3533: function (e, t, n) {
    var r = n(2793),
      o = n(2794),
      i = n(3474),
      a = n(3475),
      s = n(2877).f;
    e.exports = function (e) {
      var t = o.Symbol || (o.Symbol = i ? {} : r.Symbol || {});
      "_" == e.charAt(0) || e in t || s(t, e, {value: a.f(e)});
    };
  },
  3534: function (e, t) {
    var n = Math.ceil,
      r = Math.floor;
    e.exports = function (e) {
      return isNaN((e = +e)) ? 0 : (e > 0 ? r : n)(e);
    };
  },
  3535: function (e, t, n) {
    var r = n(3531)("keys"),
      o = n(3473);
    e.exports = function (e) {
      return r[e] || (r[e] = o(e));
    };
  },
  3536: function (e, t) {
    e.exports =
      "constructor,hasOwnProperty,isPrototypeOf,propertyIsEnumerable,toLocaleString,toString,valueOf".split(
        ","
      );
  },
  3537: function (e, t) {
    t.f = {}.propertyIsEnumerable;
  },
  3538: function (e, t) {
    e.exports = {};
  },
  3542: function (e, t, n) {
    var r = n(3529);
    e.exports = function (e) {
      return Object(r(e));
    };
  },
  364: function (e, t, n) {
    "use strict";
    (function (e) {
      Object.defineProperty(t, "__esModule", {value: !0}),
        (t.TRUSTED_POSTMESSAGE_HOSTS =
          t.PLAID_INTERNAL_NAMESPACE =
          t.LINK_WEB_SDK_VERSION =
          t.LINK_OPEN_HTML_PATH =
          t.LINK_IFRAME_SANDBOX_PERMISSIONS =
          t.LINK_IFRAME_FEATURE_POLICY_URLS =
          t.LINK_IFRAME_ALLOW =
          t.LINK_HTML_PATH =
          t.LINK_CLIENT_URL =
          t.LINK_CLIENT_STABLE_URL =
          t.LINK_CLIENT_CORS_ORIGIN =
          t.EMBEDDED_LINK_HTML_PATH =
          t.CREATE_PARAMETERS =
            void 0),
        n(2),
        n(3);
      var r = n(500);
      const o = String("https://cdn.plaid.com/link/2.0.3119");
      t.LINK_CLIENT_URL = o;
      const i = String("https://cdn.plaid.com/link/v2/stable");
      t.LINK_CLIENT_STABLE_URL = i;
      t.LINK_HTML_PATH = "/link.html";
      t.EMBEDDED_LINK_HTML_PATH = "/embedded-link-app.html";
      t.LINK_OPEN_HTML_PATH = "/link-open.html";
      t.PLAID_INTERNAL_NAMESPACE = "plaid_link";
      t.CREATE_PARAMETERS = [
        "env",
        "onEvent",
        "onExit",
        "onLoad",
        "onSuccess",
        "receivedRedirectUri",
        "token",
      ];
      const a = String("https://cdn.plaid.com");
      t.LINK_CLIENT_CORS_ORIGIN = a;
      const s = e.env.LINK_WEB_SDK_VERSION;
      t.LINK_WEB_SDK_VERSION = s;
      const u = new Set([
        "secure.plaid.com",
        "cdn.plaid.com",
        "verify.plaid.com",
        "verify-east.plaid.com",
        "verify-sandbox.plaid.com",
        "verify-sandbox-east.plaid.com",
        "flow.cognitohq.com",
        "flow-east.cognitohq.com",
        "flow-sandbox.cognitohq.com",
        "flow-sandbox-east.cognitohq.com",
        ...r.TESTING_POSTMESSAGE_HOSTS,
      ]);
      t.TRUSTED_POSTMESSAGE_HOSTS = u;
      const c = [
        "https://cdn-testing.plaid.com",
        "https://cdn.plaid.com",
        "https://secure.plaid.com",
        "https://secure-testing.plaid.com",
        "https://verify.plaid.com",
        "https://verify-sandbox.plaid.com",
        "https://verify-testing.plaid.com",
      ].join(" ");
      t.LINK_IFRAME_FEATURE_POLICY_URLS = c;
      const l = [`camera 'src' ${c}`, `clipboard-write ${c}`].join("; ");
      t.LINK_IFRAME_ALLOW = l;
      t.LINK_IFRAME_SANDBOX_PERMISSIONS =
        "allow-downloads allow-forms allow-modals allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-scripts allow-top-navigation";
    }).call(this, n(220));
  },
  37: function (e, t, n) {
    "use strict";
    var r = n(267),
      o = n(28),
      i = n(21),
      a = n(480),
      s = n(22),
      u = n(55),
      c = n(23),
      l = n(159),
      d = n(131),
      f = n(229),
      p = n(80),
      v = n(149),
      _ = n(481),
      y = n(197),
      h = n(498),
      g = n(482),
      b = n(27)("replace"),
      E = Math.max,
      m = Math.min,
      w = i([].concat),
      O = i([].push),
      S = i("".indexOf),
      I = i("".slice),
      P = "$0" === "a".replace(/./, "$0"),
      T = !!/./[b] && "" === /./[b]("a", "$0");
    a(
      "replace",
      function (e, t, n) {
        var i = T ? "$" : "$0";
        return [
          function replace(e, n) {
            var r = v(this),
              i = l(e) ? void 0 : y(e, b);
            return i ? o(i, e, r, n) : o(t, p(r), e, n);
          },
          function (e, o) {
            var a = u(this),
              s = p(e);
            if ("string" == typeof o && -1 === S(o, i) && -1 === S(o, "$<")) {
              var l = n(t, a, s, o);
              if (l.done) return l.value;
            }
            var v = c(o);
            v || (o = p(o));
            var y,
              b = a.global;
            b && ((y = a.unicode), (a.lastIndex = 0));
            for (var P, T = []; null !== (P = g(a, s)) && (O(T, P), b); ) {
              "" === p(P[0]) && (a.lastIndex = _(s, f(a.lastIndex), y));
            }
            for (var L, x = "", A = 0, N = 0; N < T.length; N++) {
              for (
                var R,
                  k = p((P = T[N])[0]),
                  C = E(m(d(P.index), s.length), 0),
                  M = [],
                  j = 1;
                j < P.length;
                j++
              )
                O(M, void 0 === (L = P[j]) ? L : String(L));
              var D = P.groups;
              if (v) {
                var U = w([k], M, C, s);
                void 0 !== D && O(U, D), (R = p(r(o, void 0, U)));
              } else R = h(k, s, C, M, D, o);
              C >= A && ((x += I(s, A, C) + R), (A = C + k.length));
            }
            return x + I(s, A);
          },
        ];
      },
      !!s(function () {
        var e = /./;
        return (
          (e.exec = function () {
            var e = [];
            return (e.groups = {a: "7"}), e;
          }),
          "7" !== "".replace(e, "$<a>")
        );
      }) ||
        !P ||
        T
    );
  },
  3733: function (e, t, n) {
    "use strict";
    Object.defineProperty(t, "__esModule", {value: !0}),
      (t.setStyles = t.renderedPreload = t.FULL_SCREEN_STYLES = void 0),
      n(13);
    t.FULL_SCREEN_STYLES = {
      position: "fixed",
      top: "0",
      left: "0",
      right: "0",
      bottom: "0",
      "z-index": "9999999999",
      "border-width": "0",
      display: "none",
      "overflow-x": "hidden",
      "overflow-y": "auto",
    };
    const setStyles = (e, t, n) => {
      for (const r in t) e.style.setProperty(r, t[r], n);
    };
    t.setStyles = setStyles;
    const r = {inert: "", tabindex: "-1", "aria-hidden": "true"};
    t.renderedPreload = (e, t, n) => {
      const o = String(window.navigator && navigator.userAgent);
      if (
        !0 !== t ||
        !/android|silk/i.test(o) ||
        /windows phone/i.test(o) ||
        /; wv\)/.test(o)
      )
        return;
      const i = Object.assign({}, n, {
        display: "block",
        opacity: "0",
        "pointer-events": "none",
      });
      setStyles(e, i, "important");
      for (const t in r) e.setAttribute(t, r[t]);
      return () => {
        for (const t in i) e.style.removeProperty(t);
        for (const t in r) e.removeAttribute(t);
      };
    };
  },
  3734: function (e, t, n) {
    "use strict";
    Object.defineProperty(t, "__esModule", {value: !0}), (t.emitLinkOpen = void 0);
    var r = n(364),
      o = n(3733);
    t.emitLinkOpen = (e) => {
      const t = document.createElement("iframe");
      (t.id = "plaid-link-open-iframe"),
        (t.title = "Plaid Link Open"),
        (t.src = e),
        (t.allow = r.LINK_IFRAME_ALLOW),
        t.setAttribute("sandbox", r.LINK_IFRAME_SANDBOX_PERMISSIONS),
        (t.width = "100%"),
        (t.height = "100%"),
        (0, o.setStyles)(t, o.FULL_SCREEN_STYLES),
        (t.onload = () => {
          t.parentNode && t.parentNode.removeChild(t);
        }),
        document.body.appendChild(t);
    };
  },
  3735: function (e, t, n) {
    "use strict";
    Object.defineProperty(t, "__esModule", {value: !0});
    var r = {
      getMetaViewport: !0,
      isInlineStylesheetSupported: !0,
      isMetaViewportSet: !0,
      isInIframe: !0,
    };
    (t.isMetaViewportSet =
      t.isInlineStylesheetSupported =
      t.isInIframe =
      t.getMetaViewport =
        void 0),
      n(13);
    var o = n(4394);
    Object.keys(o).forEach(function (e) {
      "default" !== e &&
        "__esModule" !== e &&
        (Object.prototype.hasOwnProperty.call(r, e) ||
          (e in t && t[e] === o[e]) ||
          Object.defineProperty(t, e, {
            enumerable: !0,
            get: function () {
              return o[e];
            },
          }));
    });
    const getMetaViewport = () => {
      const e = document.querySelectorAll('meta[name="viewport"]');
      if (0 === e.length) return "";
      const t = e[e.length - 1].getAttribute("content");
      return String(t);
    };
    t.getMetaViewport = getMetaViewport;
    t.isInlineStylesheetSupported = () => {
      try {
        const e = `link-stylesheet-test-${Math.floor(100 * Math.random())}`,
          t = document.createElement("div");
        t.id = e;
        const n = document.createElement("style");
        n.textContent = `#${e} { width: 100px; height: 100px; }`;
        const r = document.body;
        r.appendChild(t), r.appendChild(n);
        const o = 100 === t.offsetWidth;
        return r.removeChild(t), r.removeChild(n), o;
      } catch (e) {
        return !1;
      }
    };
    t.isMetaViewportSet = () => /device-width/.test(getMetaViewport());
    t.isInIframe = () => {
      try {
        return window.self !== window.top;
      } catch (e) {
        return;
      }
    };
  },
  3736: function (e, t, n) {
    "use strict";
    Object.defineProperty(t, "__esModule", {value: !0}),
      (t.FLEX_LINK_HTML_PATH = t.CREATE_PARAMETERS = void 0),
      Object.defineProperty(t, "LINK_CLIENT_CORS_ORIGIN", {
        enumerable: !0,
        get: function () {
          return r.LINK_CLIENT_CORS_ORIGIN;
        },
      }),
      Object.defineProperty(t, "LINK_CLIENT_STABLE_URL", {
        enumerable: !0,
        get: function () {
          return r.LINK_CLIENT_STABLE_URL;
        },
      }),
      Object.defineProperty(t, "LINK_CLIENT_URL", {
        enumerable: !0,
        get: function () {
          return r.LINK_CLIENT_URL;
        },
      }),
      Object.defineProperty(t, "LINK_HTML_PATH", {
        enumerable: !0,
        get: function () {
          return r.LINK_HTML_PATH;
        },
      }),
      Object.defineProperty(t, "PLAID_INTERNAL_NAMESPACE", {
        enumerable: !0,
        get: function () {
          return r.PLAID_INTERNAL_NAMESPACE;
        },
      }),
      n(2),
      n(3);
    var r = n(364);
    t.FLEX_LINK_HTML_PATH = "/flink.html";
    const o = [
      ...r.CREATE_PARAMETERS,
      "apiVersion",
      "clientName",
      "configUserId",
      "configUserTags",
      "countryCodes",
      "customizations",
      "depositSwitchToken",
      "experimentVariants",
      "forceIframe",
      "hostedLinkVersion",
      "isEmbedded",
      "isSimpleIntegration",
      "key",
      "language",
      "linkCustomizationName",
      "longtail",
      "longTail",
      "oauthNonce",
      "oauthStateId",
      "oauthRedirectUri",
      "onResult",
      "paymentToken",
      "product",
      "accountSubtypes",
      "selectAccount",
      "noLoadingState",
      "useMobileWindow",
      "user",
      "userLegalName",
      "userEmailAddress",
      "userPhoneNumber",
      "webhook",
      "workflowVersionOverride",
    ];
    t.CREATE_PARAMETERS = o;
  },
  399: function (e, t, n) {
    "use strict";
    var r = n(90),
      o = n(21);
    e.exports = function (e) {
      if ("Function" === r(e)) return o(e);
    };
  },
  4: function (e, t) {
    (e.exports = function _interopRequireDefault(e) {
      return e && e.__esModule ? e : {default: e};
    }),
      (e.exports.__esModule = !0),
      (e.exports.default = e.exports);
  },
  405: function (e, t, n) {
    "use strict";
    var r = n(28),
      o = n(51),
      i = n(216),
      a = n(197),
      s = n(485),
      u = n(27),
      c = TypeError,
      l = u("toPrimitive");
    e.exports = function (e, t) {
      if (!o(e) || i(e)) return e;
      var n,
        u = a(e, l);
      if (u) {
        if ((void 0 === t && (t = "default"), (n = r(u, e, t)), !o(n) || i(n)))
          return n;
        throw new c("Can't convert object to primitive value");
      }
      return void 0 === t && (t = "number"), s(e, t);
    };
  },
  406: function (e, t, n) {
    "use strict";
    var r = n(131),
      o = Math.max,
      i = Math.min;
    e.exports = function (e, t) {
      var n = r(e);
      return n < 0 ? o(n + t, 0) : i(n, t);
    };
  },
  407: function (e, t, n) {
    "use strict";
    var r = n(76);
    e.exports = function (e, t, n) {
      for (var o in t) r(e, o, t[o], n);
      return e;
    };
  },
  413: function (e, t, n) {
    "use strict";
    var r = {};
    (r[n(27)("toStringTag")] = "z"), (e.exports = "[object z]" === String(r));
  },
  4304: function (e, t, n) {
    "use strict";
    Object.defineProperty(t, "__esModule", {value: !0}),
      (t.ProviderRpcErrorCode = t.ChainTypes = void 0);
    let r = (function (e) {
      return (
        (e[(e.ACCOUNT_ACCESS_REJECTED = 4001)] = "ACCOUNT_ACCESS_REJECTED"),
        (e[(e.ACCOUNT_ACCESS_ALREADY_REQUESTED = -32002)] =
          "ACCOUNT_ACCESS_ALREADY_REQUESTED"),
        (e[(e.UNAUTHORIZED = 4100)] = "UNAUTHORIZED"),
        (e[(e.INVALID_PARAMS = -32602)] = "INVALID_PARAMS"),
        (e[(e.UNSUPPORTED_METHOD = 4200)] = "UNSUPPORTED_METHOD"),
        (e[(e.DISCONNECTED = 4900)] = "DISCONNECTED"),
        (e[(e.CHAIN_DISCONNECTED = 4901)] = "CHAIN_DISCONNECTED"),
        (e[(e.CHAIN_NOT_ADDED = 4902)] = "CHAIN_NOT_ADDED"),
        (e[(e.DOES_NOT_EXIST = -32601)] = "DOES_NOT_EXIST"),
        (e[(e.METAMASK_NETWORK_SWITCH_DISCONNECT = 1013)] =
          "METAMASK_NETWORK_SWITCH_DISCONNECT"),
        e
      );
    })({});
    t.ProviderRpcErrorCode = r;
    let o = (function (e) {
      return (e[(e.Unknown = 0)] = "Unknown"), (e[(e.EVM = 1)] = "EVM"), e;
    })({});
    t.ChainTypes = o;
  },
  4306: function (e, t, n) {
    e.exports =
      !n(2878) &&
      !n(3099)(function () {
        return (
          7 !=
          Object.defineProperty(n(4307)("div"), "a", {
            get: function () {
              return 7;
            },
          }).a
        );
      });
  },
  4307: function (e, t, n) {
    var r = n(3100),
      o = n(2793).document,
      i = r(o) && r(o.createElement);
    e.exports = function (e) {
      return i ? o.createElement(e) : {};
    };
  },
  4308: function (e, t, n) {
    var r = n(4435),
      o = n(4451);
    function _typeof(t) {
      return (
        (e.exports = _typeof =
          "function" == typeof r && "symbol" == typeof o
            ? function (e) {
                return typeof e;
              }
            : function (e) {
                return e &&
                  "function" == typeof r &&
                  e.constructor === r &&
                  e !== r.prototype
                  ? "symbol"
                  : typeof e;
              }),
        (e.exports.__esModule = !0),
        (e.exports.default = e.exports),
        _typeof(t)
      );
    }
    (e.exports = _typeof), (e.exports.__esModule = !0), (e.exports.default = e.exports);
  },
  4309: function (e, t, n) {
    e.exports = n(3074);
  },
  4310: function (e, t, n) {
    var r = n(2879),
      o = n(3076),
      i = n(4440)(!1),
      a = n(3535)("IE_PROTO");
    e.exports = function (e, t) {
      var n,
        s = o(e),
        u = 0,
        c = [];
      for (n in s) n != a && r(s, n) && c.push(n);
      for (; t.length > u; ) r(s, (n = t[u++])) && (~i(c, n) || c.push(n));
      return c;
    };
  },
  4311: function (e, t) {
    var n = {}.toString;
    e.exports = function (e) {
      return n.call(e).slice(8, -1);
    };
  },
  4312: function (e, t) {
    t.f = Object.getOwnPropertySymbols;
  },
  4313: function (e, t, n) {
    var r = n(3471),
      o = n(4444),
      i = n(3536),
      a = n(3535)("IE_PROTO"),
      Empty = function () {},
      createDict = function () {
        var e,
          t = n(4307)("iframe"),
          r = i.length;
        for (
          t.style.display = "none",
            n(4445).appendChild(t),
            t.src = "javascript:",
            (e = t.contentWindow.document).open(),
            e.write("<script>document.F=Object</script>"),
            e.close(),
            createDict = e.F;
          r--;

        )
          delete createDict.prototype[i[r]];
        return createDict();
      };
    e.exports =
      Object.create ||
      function create(e, t) {
        var n;
        return (
          null !== e
            ? ((Empty.prototype = r(e)),
              (n = new Empty()),
              (Empty.prototype = null),
              (n[a] = e))
            : (n = createDict()),
          void 0 === t ? n : o(n, t)
        );
      };
  },
  4314: function (e, t, n) {
    var r = n(4310),
      o = n(3536).concat("length", "prototype");
    t.f =
      Object.getOwnPropertyNames ||
      function getOwnPropertyNames(e) {
        return r(e, o);
      };
  },
  4315: function (e, t, n) {
    "use strict";
    var r = n(3474),
      o = n(3470),
      i = n(4309),
      a = n(3074),
      s = n(3538),
      u = n(4455),
      c = n(3532),
      l = n(4456),
      d = n(3075)("iterator"),
      f = !([].keys && "next" in [].keys()),
      p = "keys",
      v = "values",
      returnThis = function () {
        return this;
      };
    e.exports = function (e, t, n, _, y, h, g) {
      u(n, t, _);
      var b,
        E,
        m,
        getMethod = function (e) {
          if (!f && e in I) return I[e];
          switch (e) {
            case p:
              return function keys() {
                return new n(this, e);
              };
            case v:
              return function values() {
                return new n(this, e);
              };
          }
          return function entries() {
            return new n(this, e);
          };
        },
        w = t + " Iterator",
        O = y == v,
        S = !1,
        I = e.prototype,
        P = I[d] || I["@@iterator"] || (y && I[y]),
        T = P || getMethod(y),
        L = y ? (O ? getMethod("entries") : T) : void 0,
        x = ("Array" == t && I.entries) || P;
      if (
        (x &&
          (m = l(x.call(new e()))) !== Object.prototype &&
          m.next &&
          (c(m, w, !0), r || "function" == typeof m[d] || a(m, d, returnThis)),
        O &&
          P &&
          P.name !== v &&
          ((S = !0),
          (T = function values() {
            return P.call(this);
          })),
        (r && !g) || (!f && !S && I[d]) || a(I, d, T),
        (s[t] = T),
        (s[w] = returnThis),
        y)
      )
        if (
          ((b = {values: O ? T : getMethod(v), keys: h ? T : getMethod(p), entries: L}),
          g)
        )
          for (E in b) E in I || i(I, E, b[E]);
        else o(o.P + o.F * (f || S), t, b);
      return b;
    };
  },
  4317: function (e, t, n) {
    "use strict";
    var r = n(2793),
      o = n(2879),
      i = n(2878),
      a = n(3470),
      s = n(4309),
      u = n(4437).KEY,
      c = n(3099),
      l = n(3531),
      d = n(3532),
      f = n(3473),
      p = n(3075),
      v = n(3475),
      _ = n(3533),
      y = n(4438),
      h = n(4443),
      g = n(3471),
      b = n(3100),
      E = n(3542),
      m = n(3076),
      w = n(3530),
      O = n(3472),
      S = n(4313),
      I = n(4446),
      P = n(4447),
      T = n(4312),
      L = n(2877),
      x = n(3477),
      A = P.f,
      N = L.f,
      R = I.f,
      k = r.Symbol,
      C = r.JSON,
      M = C && C.stringify,
      j = p("_hidden"),
      D = p("toPrimitive"),
      U = {}.propertyIsEnumerable,
      W = l("symbol-registry"),
      V = l("symbols"),
      K = l("op-symbols"),
      H = Object.prototype,
      B = "function" == typeof k && !!T.f,
      q = r.QObject,
      G = !q || !q.prototype || !q.prototype.findChild,
      z =
        i &&
        c(function () {
          return (
            7 !=
            S(
              N({}, "a", {
                get: function () {
                  return N(this, "a", {value: 7}).a;
                },
              })
            ).a
          );
        })
          ? function (e, t, n) {
              var r = A(H, t);
              r && delete H[t], N(e, t, n), r && e !== H && N(H, t, r);
            }
          : N,
      wrap = function (e) {
        var t = (V[e] = S(k.prototype));
        return (t._k = e), t;
      },
      $ =
        B && "symbol" == typeof k.iterator
          ? function (e) {
              return "symbol" == typeof e;
            }
          : function (e) {
              return e instanceof k;
            },
      Q = function defineProperty(e, t, n) {
        return (
          e === H && Q(K, t, n),
          g(e),
          (t = w(t, !0)),
          g(n),
          o(V, t)
            ? (n.enumerable
                ? (o(e, j) && e[j][t] && (e[j][t] = !1),
                  (n = S(n, {enumerable: O(0, !1)})))
                : (o(e, j) || N(e, j, O(1, {})), (e[j][t] = !0)),
              z(e, t, n))
            : N(e, t, n)
        );
      },
      X = function defineProperties(e, t) {
        g(e);
        for (var n, r = y((t = m(t))), o = 0, i = r.length; i > o; )
          Q(e, (n = r[o++]), t[n]);
        return e;
      },
      Y = function propertyIsEnumerable(e) {
        var t = U.call(this, (e = w(e, !0)));
        return (
          !(this === H && o(V, e) && !o(K, e)) &&
          (!(t || !o(this, e) || !o(V, e) || (o(this, j) && this[j][e])) || t)
        );
      },
      J = function getOwnPropertyDescriptor(e, t) {
        if (((e = m(e)), (t = w(t, !0)), e !== H || !o(V, t) || o(K, t))) {
          var n = A(e, t);
          return !n || !o(V, t) || (o(e, j) && e[j][t]) || (n.enumerable = !0), n;
        }
      },
      Z = function getOwnPropertyNames(e) {
        for (var t, n = R(m(e)), r = [], i = 0; n.length > i; )
          o(V, (t = n[i++])) || t == j || t == u || r.push(t);
        return r;
      },
      ee = function getOwnPropertySymbols(e) {
        for (var t, n = e === H, r = R(n ? K : m(e)), i = [], a = 0; r.length > a; )
          !o(V, (t = r[a++])) || (n && !o(H, t)) || i.push(V[t]);
        return i;
      };
    B ||
      ((k = function Symbol() {
        if (this instanceof k) throw TypeError("Symbol is not a constructor!");
        var e = f(arguments.length > 0 ? arguments[0] : void 0),
          $set = function (t) {
            this === H && $set.call(K, t),
              o(this, j) && o(this[j], e) && (this[j][e] = !1),
              z(this, e, O(1, t));
          };
        return i && G && z(H, e, {configurable: !0, set: $set}), wrap(e);
      }),
      s(k.prototype, "toString", function toString() {
        return this._k;
      }),
      (P.f = J),
      (L.f = Q),
      (n(4314).f = I.f = Z),
      (n(3537).f = Y),
      (T.f = ee),
      i && !n(3474) && s(H, "propertyIsEnumerable", Y, !0),
      (v.f = function (e) {
        return wrap(p(e));
      })),
      a(a.G + a.W + a.F * !B, {Symbol: k});
    for (
      var te =
          "hasInstance,isConcatSpreadable,iterator,match,replace,search,species,split,toPrimitive,toStringTag,unscopables".split(
            ","
          ),
        ne = 0;
      te.length > ne;

    )
      p(te[ne++]);
    for (var re = x(p.store), oe = 0; re.length > oe; ) _(re[oe++]);
    a(a.S + a.F * !B, "Symbol", {
      for: function (e) {
        return o(W, (e += "")) ? W[e] : (W[e] = k(e));
      },
      keyFor: function keyFor(e) {
        if (!$(e)) throw TypeError(e + " is not a symbol!");
        for (var t in W) if (W[t] === e) return t;
      },
      useSetter: function () {
        G = !0;
      },
      useSimple: function () {
        G = !1;
      },
    }),
      a(a.S + a.F * !B, "Object", {
        create: function create(e, t) {
          return void 0 === t ? S(e) : X(S(e), t);
        },
        defineProperty: Q,
        defineProperties: X,
        getOwnPropertyDescriptor: J,
        getOwnPropertyNames: Z,
        getOwnPropertySymbols: ee,
      });
    var ie = c(function () {
      T.f(1);
    });
    a(a.S + a.F * ie, "Object", {
      getOwnPropertySymbols: function getOwnPropertySymbols(e) {
        return T.f(E(e));
      },
    }),
      C &&
        a(
          a.S +
            a.F *
              (!B ||
                c(function () {
                  var e = k();
                  return (
                    "[null]" != M([e]) || "{}" != M({a: e}) || "{}" != M(Object(e))
                  );
                })),
          "JSON",
          {
            stringify: function stringify(e) {
              for (var t, n, r = [e], o = 1; arguments.length > o; )
                r.push(arguments[o++]);
              if (((n = t = r[1]), (b(t) || void 0 !== e) && !$(e)))
                return (
                  h(t) ||
                    (t = function (e, t) {
                      if (("function" == typeof n && (t = n.call(this, e, t)), !$(t)))
                        return t;
                    }),
                  (r[1] = t),
                  M.apply(C, r)
                );
            },
          }
        ),
      k.prototype[D] || n(3074)(k.prototype, D, k.prototype.valueOf),
      d(k, "Symbol"),
      d(Math, "Math", !0),
      d(r.JSON, "JSON", !0);
  },
  437: function (e, t, n) {
    "use strict";
    var r = n(124).match(/firefox\/(\d+)/i);
    e.exports = !!r && +r[1];
  },
  438: function (e, t, n) {
    "use strict";
    var r = n(124);
    e.exports = /MSIE|Trident/.test(r);
  },
  439: function (e, t, n) {
    "use strict";
    var r = n(124).match(/AppleWebKit\/(\d+)\./);
    e.exports = !!r && +r[1];
  },
  4392: function (e, t, n) {
    "use strict";
    n(2), n(3);
    var r = n(2792);
    Object.defineProperty(t, "__esModule", {value: !0}), (t.create = void 0);
    var o = r(n(3073));
    n(69), n(13), n(37);
    var i = n(4525),
      a = n(3734),
      s = _interopRequireWildcard(n(3735)),
      u = _interopRequireWildcard(n(4396)),
      c = n(114),
      l = n(4427),
      d = n(4397),
      f = r(n(306));
    function _getRequireWildcardCache(e) {
      if ("function" != typeof WeakMap) return null;
      var t = new WeakMap(),
        n = new WeakMap();
      return (_getRequireWildcardCache = function (e) {
        return e ? n : t;
      })(e);
    }
    function _interopRequireWildcard(e, t) {
      if (!t && e && e.__esModule) return e;
      if (null === e || ("object" != typeof e && "function" != typeof e))
        return {default: e};
      var n = _getRequireWildcardCache(t);
      if (n && n.has(e)) return n.get(e);
      var r = {},
        o = Object.defineProperty && Object.getOwnPropertyDescriptor;
      for (var i in e)
        if ("default" !== i && Object.prototype.hasOwnProperty.call(e, i)) {
          var a = o ? Object.getOwnPropertyDescriptor(e, i) : null;
          a && (a.get || a.set) ? Object.defineProperty(r, i, a) : (r[i] = e[i]);
        }
      return (r.default = e), n && n.set(e, r), r;
    }
    function ownKeys(e, t) {
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
    function _objectSpread(e) {
      for (var t = 1; t < arguments.length; t++) {
        var n = null != arguments[t] ? arguments[t] : {};
        t % 2
          ? ownKeys(Object(n), !0).forEach(function (t) {
              (0, o.default)(e, t, n[t]);
            })
          : Object.getOwnPropertyDescriptors
            ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n))
            : ownKeys(Object(n)).forEach(function (t) {
                Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
              });
      }
      return e;
    }
    t.create = function (e) {
      let t = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : {};
      return (
        (t.detectedWeb3WalletIds = (0, l.getInstalledWalletPlugins)(
          t.web3ValidChains && t.web3ValidChains[0]
        )),
        (t.version = c.VERSION),
        (0, i.create)(e, t)
      );
    };
    (u.hooks.getConfig = (e, t) =>
      ((e) => {
        let {
          apiVersion: t,
          clientName: n,
          configUserId: r,
          configUserTags: o,
          countryCodes: i,
          customizations: a,
          depositSwitchToken: u,
          embeddedOpenLinkConfiguration: c,
          embeddedWorkflowSessionId: l,
          embeddedComponentConfiguration: d,
          env: p,
          experimentVariants: v,
          forceDarkMode: _,
          hostedLinkVersion: y,
          institutionContactMessagingInstitutions: h,
          isEagerStart: g,
          isEmbedded: b,
          isPrivacyPortalItemAdd: E,
          isSimpleIntegration: m,
          isUsingWalletOnboardCallback: w,
          key: O,
          language: S,
          linkOpenId: I,
          linkCustomizationName: P,
          logInternalAnalytics: T,
          oauthNonce: L,
          oauthRedirectUri: x,
          oauthStateId: A,
          onEvent: N,
          onResult: R,
          onExit: k,
          onLoad: C,
          paymentToken: M,
          product: j,
          receivedRedirectUri: D,
          accountSubtypes: U,
          selectAccount: W,
          noLoadingState: V,
          token: K,
          useMockFingerprint: H,
          hideSandboxMessage: B,
          user: q,
          userLegalName: G,
          userEmailAddress: z,
          userPhoneNumber: $,
          webhook: Q,
          workflowVersionOverride: X,
          detectedWeb3WalletIds: Y,
          web3ValidChains: J,
          version: Z,
          workflowSessionId: ee,
          continuationToken: te,
        } = e;
        return {
          apiVersion: t,
          clientName: n,
          configUserId: r,
          configUserTags: o,
          countryCodes: i,
          customizations: a,
          depositSwitchToken: u,
          embeddedOpenLinkConfiguration: c,
          embeddedComponentConfiguration: d,
          embeddedWorkflowSessionId: l,
          env: p,
          experimentVariants: v,
          forceIframe: !0,
          forceDarkMode: _,
          hostedLinkVersion: y,
          institutionContactMessagingInstitutions: h,
          isPrivacyPortalItemAdd: E,
          isEagerStart: null == g || g,
          isEmbedded: b,
          isInIframe: s.isInIframe(),
          isParentInlineStylesheetSupported: s.isInlineStylesheetSupported(),
          isParentMetaViewportSet: s.isMetaViewportSet(),
          isSimpleIntegration: !0 === m,
          isUsingOnEventCallback: "function" == typeof N,
          isUsingOnResultCallback: "function" == typeof R,
          isUsingOnExitCallback: "function" == typeof k,
          isUsingOnLoadCallback: "function" == typeof C,
          isUsingWalletOnboardCallback: w,
          key: O,
          language: S,
          linkCustomizationName: P,
          linkOpenId: null != I ? I : (0, f.default)(),
          logInternalAnalytics: !0 === T,
          oauthNonce: L,
          oauthRedirectUri: x,
          oauthStateId: A,
          parentMetaViewport: s.getMetaViewport(),
          paymentToken: M,
          product: j,
          receivedRedirectUri: D,
          accountSubtypes: U,
          selectAccount: !0 === W,
          noLoadingState: V,
          token: K,
          useMockFingerprint: H,
          hideSandboxMessage: B,
          user: q,
          userLegalName: G,
          userEmailAddress: z,
          userPhoneNumber: $,
          version: Z,
          webhook: Q,
          workflowVersionOverride: X,
          detectedWeb3WalletIds: Y,
          web3ValidChains: J,
          isLinkWebSdk: void 0,
          linkSdkVersion: void 0,
          workflowSessionId: ee,
          continuationToken: te,
        };
      })(
        _objectSpread(
          _objectSpread({}, e),
          {},
          {
            isUsingWalletOnboardCallback: !!t.onProviderSuccess,
            workflowVersionOverride: t.workflowVersionOverride,
            detectedWeb3WalletIds: t.detectedWeb3WalletIds,
            isEagerStart: t.isEagerStart,
            version: t.version,
            web3ValidChains: t.web3ValidChains,
            forceDarkMode: t.forceDarkMode,
            embeddedWorkflowSessionId: t.embeddedWorkflowSessionId,
            embeddedOpenLinkConfiguration: t.embeddedOpenLinkConfiguration,
            useMockFingerprint: t.useMockFingerprint,
            hideSandboxMessage: t.hideSandboxMessage,
            continuationToken: t.continuationToken,
            workflowSessionId: t.workflowSessionId,
          }
        )
      )),
      (u.hooks.getQueryParameters = (e) => {
        let {
          countryCodes: t,
          embeddedComponentConfiguration: n,
          env: r,
          experimentVariants: o,
          key: i,
          token: a,
          language: s,
          linkCustomizationName: u,
          origin: c,
          product: l,
          accountSubtypes: d,
          uniqueId: f,
          oauthStateId: p,
          noLoadingState: v,
          version: _,
          hostedLinkVersion: y,
          linkOpenId: h,
        } = e;
        return {
          countryCodes: t,
          embeddedComponentConfiguration: null == n ? void 0 : JSON.stringify(n),
          env: r,
          experimentVariants: null == o ? void 0 : JSON.stringify(o),
          isLinkInitialize: !0,
          key: i,
          token: a,
          language: s,
          linkCustomizationName: u,
          origin: c,
          product: l,
          accountSubtypes: JSON.stringify(d),
          uniqueId: f,
          version: _,
          oauthStateId: p,
          noLoadingState: v,
          hostedLinkVersion: y,
          linkOpenId: h,
          isLinkWebSdk: void 0,
          linkSdkVersion: void 0,
        };
      }),
      (u.hooks.validateCreateOptions = d.validateCreateOptions),
      (u.hooks.updateLinkURL = (e, t) => {
        if ("1.1.0" === t.hostedLinkVersion) {
          if (-1 !== e.indexOf("cdn.plaid.com"))
            return e.replace("cdn.plaid.com", "secure.plaid.com");
          if (-1 !== e.indexOf("cdn-testing.plaid.com"))
            return e.replace("cdn-testing.plaid.com", "secure-testing.plaid.com");
        }
        return e;
      }),
      (u.hooks.emitLinkOpen = a.emitLinkOpen),
      (u.hooks.shouldReinitializeOnOpen = (e) => null != e.embeddedWorkflowSessionId);
  },
  4393: function (e, t, n) {
    "use strict";
    Object.defineProperty(t, "__esModule", {value: !0}),
      (t.openLinkPopup = t.create = void 0);
    const openLinkPopup = (e) => {
      const t = getLinkPopupWindowFeatures();
      return window.open(e, "plaid-link-popup", t);
    };
    t.openLinkPopup = openLinkPopup;
    const getLinkPopupWindowFeatures = () =>
      `width=360,height=608,left=${window.screenX + (window.outerWidth - 360) / 2},top=${window.screenY + (window.outerHeight - 608) / 2},resizable=no,scrollbars=no`;
    t.create = () => {
      let e = null,
        t = null,
        n = !1;
      return {
        initialize: (t, n) => {
          e = t;
        },
        show: () => {
          e && (t = openLinkPopup(e));
        },
        hide: () => {
          null != t && t.close(), (n = !1);
        },
        destroy: () => {
          null != t && t.close(), (n = !1);
        },
        refresh: () => {},
        isOpen: () => n,
        postMessage: (e, n) => {
          null != t && t.postMessage(e, n);
        },
        resize: () => {},
        window: () => t,
      };
    };
  },
  4394: function (e, t, n) {
    "use strict";
    Object.defineProperty(t, "__esModule", {value: !0}),
      (t.uuid =
        t.sendMessage =
        t.queryStringFromQueryParameters =
        t.isTrustedPostmessageOrigin =
        t.isMessageFromLinkWindow =
        t.getWindowOrigin =
        t.default =
        t.createPostmessageMismatchReporter =
        t.createMessageEventListener =
        t.buildLinkUrl =
          void 0),
      n(69),
      n(13),
      n(2),
      n(3),
      n(93),
      n(37);
    var r = n(364);
    t.buildLinkUrl = function (e) {
      let t =
        arguments.length > 1 && void 0 !== arguments[1]
          ? arguments[1]
          : {
              LINK_CLIENT_URL: r.LINK_CLIENT_URL,
              LINK_CLIENT_STABLE_URL: r.LINK_CLIENT_STABLE_URL,
              LINK_HTML_PATH: r.LINK_HTML_PATH,
            };
      const n = queryStringFromQueryParameters(e),
        o =
          t.LINK_CLIENT_STABLE_URL.length > 0
            ? t.LINK_CLIENT_STABLE_URL
            : t.LINK_CLIENT_URL,
        i = t.LINK_HTML_PATH;
      return `${o}${i}?${n}`;
    };
    t.getWindowOrigin = () =>
      null != window.location.origin
        ? window.location.origin
        : window.location.protocol +
          "//" +
          window.location.hostname +
          (window.location.port ? ":" + window.location.port : "");
    const sendMessage = function (e) {
      let t = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : void 0;
      return (n) => {
        const o = Object.assign({}, n, {
          action: `${r.PLAID_INTERNAL_NAMESPACE}::${n.action}`,
        });
        e.postMessage(JSON.stringify(o), t || r.LINK_CLIENT_CORS_ORIGIN);
      };
    };
    t.sendMessage = sendMessage;
    const parseOrigin = (e) => {
        if (!/^https?:\/\//i.test(e)) return null;
        const t = document.createElement("a");
        return (
          (t.href = e),
          "" === t.hostname
            ? null
            : {
                origin: `${t.protocol}//${t.hostname}${"" === t.port ? "" : `:${t.port}`}`,
                protocol: t.protocol,
                hostname: t.hostname,
                port: t.port,
              }
        );
      },
      isTrustedPostmessageOrigin = (e, t) => {
        const n = parseOrigin(t);
        if ("" !== e && e === (null == n ? void 0 : n.origin)) return !0;
        const o = parseOrigin(e);
        return (
          "https:" === (null == o ? void 0 : o.protocol) &&
          "" === o.port &&
          r.TRUSTED_POSTMESSAGE_HOSTS.has(o.hostname)
        );
      };
    t.isTrustedPostmessageOrigin = isTrustedPostmessageOrigin;
    const isMessageFromLinkWindow = (e, t) => {
      const n = t.window();
      return null != n && e.source === n;
    };
    t.isMessageFromLinkWindow = isMessageFromLinkWindow;
    t.createPostmessageMismatchReporter = (e, t) => {
      const n = new Set();
      return (r) => {
        const o = [
          r.eventOrigin,
          r.attemptedAction,
          r.sourcePresent,
          r.sourceMatchesExpectedWindow,
          r.originAllowed,
        ].join("\n");
        n.has(o) ||
          (n.add(o),
          sendMessage(
            e,
            t
          )({
            action: "postmessage-mismatch",
            eventOrigin: r.eventOrigin,
            attemptedAction: r.attemptedAction,
            sourceMatchesExpectedWindow: r.sourceMatchesExpectedWindow,
            sourcePresent: r.sourcePresent,
            originAllowed: r.originAllowed,
          }));
      };
    };
    t.createMessageEventListener = (e, t, n, r, o, i) => (a) => {
      const s = ((e) => {
        try {
          return JSON.parse(e);
        } catch (e) {
          return {};
        }
      })(a.data);
      for (const u in n) {
        const c = `${e}-${t}::${u}`;
        if (s.action !== c) continue;
        const l = null != a.source,
          d = isMessageFromLinkWindow(a, r),
          f = isTrustedPostmessageOrigin(a.origin, o);
        return d && f
          ? n[u](s)
          : void i({
              eventOrigin: a.origin,
              attemptedAction: c,
              sourceMatchesExpectedWindow: d,
              sourcePresent: l,
              originAllowed: f,
            });
      }
    };
    const queryStringFromQueryParameters = (e) => {
      const t = new URLSearchParams();
      for (const [n, r] of Object.entries(e))
        if (null != r)
          if (Array.isArray(r)) {
            if (r.length > 0) for (const e of r) null != e && t.append(n, e);
          } else "boolean" == typeof r ? t.append(n, String(r)) : t.append(n, r);
      return t.toString();
    };
    t.queryStringFromQueryParameters = queryStringFromQueryParameters;
    const uuid = () => {
      const e = window.crypto || window.msCrypto;
      return null != e && "randomUUID" in e
        ? e.randomUUID()
        : "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (e) {
            const t = (16 * Math.random()) | 0;
            return ("x" === e ? t : (3 & t) | 8).toString(16);
          });
    };
    t.uuid = uuid;
    var o = uuid;
    t.default = o;
  },
  4395: function (e, t, n) {
    "use strict";
    Object.defineProperty(t, "__esModule", {value: !0}),
      (t.messageHandlerExtensions = t.hooks = void 0);
    t.messageHandlerExtensions = {};
    t.hooks = {
      getConfig: null,
      getQueryParameters: null,
      validateCreateOptions: null,
      updateLinkURL: null,
      emitLinkOpen: null,
      shouldReinitializeOnOpen: null,
    };
  },
  4396: function (e, t, n) {
    "use strict";
    Object.defineProperty(t, "__esModule", {value: !0});
    var r = n(4395);
    Object.keys(r).forEach(function (e) {
      "default" !== e &&
        "__esModule" !== e &&
        ((e in t && t[e] === r[e]) ||
          Object.defineProperty(t, e, {
            enumerable: !0,
            get: function () {
              return r[e];
            },
          }));
    });
  },
  4397: function (e, t, n) {
    "use strict";
    Object.defineProperty(t, "__esModule", {value: !0}),
      (t.validateEmbeddedComponentConfiguration = t.validateCreateOptions = void 0);
    var r = n(3736);
    const getValidationHandlers = (e) => {
      let {env: t} = e;
      return {
        error: (e) => {
          if ("production" !== t) throw new Error(e);
        },
        warn: (e) => {
          "production" !== t && console.warn(e);
        },
      };
    };
    t.validateCreateOptions = (e) => {
      const {error: t, warn: n} = getValidationHandlers(e);
      ((e) => {
        const {warn: t} = getValidationHandlers(e);
        for (const n in e)
          r.CREATE_PARAMETERS.indexOf(n) < 0 &&
            t(`Invalid Link parameter: ${n} is not a valid Plaid.create() parameter`);
      })(e),
        "function" != typeof e.onSuccess && t("Invalid onSuccess function"),
        void 0 !== e.forceIframe &&
          n(
            "The forceIframe option has been deprecated. Link will use an iframe by default when possible."
          ),
        null == e.key &&
          null == e.token &&
          null == e.receivedRedirectUri &&
          t(
            "Missing Link parameter. Link requires a key, token, or received redirect URI to be provided."
          );
    };
    t.validateEmbeddedComponentConfiguration = (e) => {
      switch (null == e ? void 0 : e.type) {
        case "button":
          return {button_component_configuration: {}};
        case "mini_card":
          return {mini_card_component_configuration: {}};
        case "institution_select":
          return {institution_select_component_configuration: {}};
        case "chip":
          return {chip_component_configuration: {}};
      }
      return null;
    };
  },
  4425: function (e, t, n) {
    "use strict";
    Object.defineProperty(t, "__esModule", {value: !0}),
      (t.WalletConnectBrand =
        t.UnidentifiedWalletBrand =
        t.UnidentifiedPluginWallet =
        t.UnidentifiedMobileBrowserWallet =
        t.TrustWalletBrandId =
          void 0);
    t.UnidentifiedWalletBrand = "wallet_240";
    t.UnidentifiedMobileBrowserWallet = "wallet_380";
    t.UnidentifiedPluginWallet = "wallet_381";
    t.WalletConnectBrand = "wallet_235";
    t.TrustWalletBrandId = "wallet_2";
  },
  4426: function (e, t, n) {
    "use strict";
    Object.defineProperty(t, "__esModule", {value: !0}),
      (t.default = function determineChainTypeFromChainId(e) {
        const t = e.split(":");
        if (t.length < 2)
          return "0x" === e.substring(0, 2) ? r.ChainTypes.EVM : r.ChainTypes.Unknown;
        switch (t[0]) {
          case "eip155":
          case "EIP155":
            return r.ChainTypes.EVM;
          default:
            return r.ChainTypes.Unknown;
        }
      });
    var r = n(4304);
  },
  4427: function (e, t, n) {
    "use strict";
    var r = n(2792);
    Object.defineProperty(t, "__esModule", {value: !0}),
      (t.getProviderByChainType =
        t.getInstalledWalletPlugins =
        t.getEIP1193ProviderByWalletBrandId =
          void 0),
      n(148),
      n(2),
      n(3),
      n(96);
    var o = n(4425),
      i = r(n(264)),
      a = n(4304),
      s = r(n(4426));
    const u = [
        "isMetaMask",
        "isBraveWallet",
        "isCoinbaseWallet",
        "isCoinbaseBrowser",
        "isRabby",
        "__XDEFI",
        "isXDEFI",
        "isGamestop",
        "isBitKeep",
        "isBitKeepChrome",
        "isMathWallet",
        "isTokenary",
        "isTally",
        "isAlphaWallet",
        "isBitpie",
        "isBlockWallet",
        "isExodus",
        "isHbWallet",
        "isImToken",
        "isLiquality",
        "isTrust",
        "isTrustWallet",
        "isOneInchIOSWallet",
        "isOneInchAndroidWallet",
        "isTokenPocket",
        "isSequence",
        "isDfox",
        "isDeficonnectProvider",
        "isPhantom",
        "isSolflare",
        "isGlow",
      ].sort(),
      c = new Map(
        Object.entries({
          isMetaMask: "wallet_347",
          [["isBraveWallet", "isMetaMask"].toString()]: "wallet_375",
          [["isBraveWallet", "isPhantom"].toString()]: "wallet_375",
          [["__XDEFI", "isXDEFI"].toString()]: "wallet_343",
          [["__XDEFI", "isMetaMask"].toString()]: "wallet_343",
          [["isMetaMask", "isRabby"].toString()]: "wallet_353",
          [["isBitKeep", "isBitKeepChrome", "isMetaMask"].toString()]: "wallet_354",
          [["isMathWallet", "isMetaMask"].toString()]: "wallet_349",
          [["isMetaMask", "isTokenary"].toString()]: "wallet_351",
          [["isDeficonnectProvider", "isMetaMask"].toString()]: "wallet_356",
          isCoinbaseWallet: "wallet_374",
          isGamestop: "wallet_344",
          isTally: "wallet_345",
          isBlockWallet: "wallet_340",
          isLiquality: "wallet_342",
          [["isDfox", "isMetaMask", "isTokenPocket"].toString()]: "wallet_348",
          [["isTrust", "isTrustWallet"].toString()]: "wallet_355",
          isPhantom: "wallet_420",
          [["isPhantom", "isGlow"].toString()]: "wallet_411",
        })
      ),
      l = [
        {
          walletId: "wallet_374",
          brandId: "wallet_236",
          providerPath: ["coinbaseWalletExtension"],
          injectedProviderChainType: a.ChainTypes.EVM,
        },
        {
          walletId: "wallet_345",
          brandId: "wallet_233",
          providerPath: ["tally"],
          injectedProviderChainType: a.ChainTypes.EVM,
        },
        {
          walletId: "wallet_347",
          brandId: "wallet_4",
          injectedProviderChainType: a.ChainTypes.EVM,
        },
        {
          walletId: "wallet_354",
          brandId: "wallet_126",
          providerPath: ["bitkeep", "ethereum"],
          injectedProviderChainType: a.ChainTypes.EVM,
        },
        {
          walletId: "wallet_344",
          brandId: "wallet_232",
          providerPath: ["gamestop"],
          injectedProviderChainType: a.ChainTypes.EVM,
        },
        {
          walletId: "wallet_343",
          brandId: "wallet_231",
          injectedProviderChainType: a.ChainTypes.EVM,
        },
        {
          walletId: "wallet_349",
          brandId: "wallet_13",
          injectedProviderChainType: a.ChainTypes.EVM,
        },
        {
          walletId: "wallet_348",
          brandId: "wallet_11",
          injectedProviderChainType: a.ChainTypes.EVM,
        },
        {
          walletId: "wallet_353",
          brandId: "wallet_70",
          injectedProviderChainType: a.ChainTypes.EVM,
        },
        {
          walletId: "wallet_340",
          brandId: "wallet_229",
          injectedProviderChainType: a.ChainTypes.EVM,
        },
        {
          walletId: "wallet_341",
          brandId: "wallet_129",
          providerPath: ["exodus", "ethereum"],
          injectedProviderChainType: a.ChainTypes.EVM,
        },
        {
          walletId: "wallet_342",
          brandId: "wallet_230",
          injectedProviderChainType: a.ChainTypes.EVM,
        },
        {
          walletId: "wallet_375",
          brandId: "wallet_237",
          injectedProviderChainType: a.ChainTypes.EVM,
        },
        {
          walletId: "wallet_355",
          brandId: "wallet_2",
          providerPath: ["trustwallet"],
          injectedProviderChainType: a.ChainTypes.EVM,
        },
        {
          walletId: "wallet_356",
          brandId: "wallet_6",
          providerPath: ["deficonnectProvider"],
          injectedProviderChainType: a.ChainTypes.EVM,
        },
      ],
      d = new Map(
        Object.entries({
          isMetaMask: "wallet_358",
          isCoinbaseWallet: "wallet_374",
          [["isCoinbaseBrowser", "isCoinbaseWallet"].toString()]: "wallet_372",
          isAlphaWallet: "wallet_364",
          isBitpie: "wallet_368",
          isHbWallet: "wallet_362",
          isImToken: "wallet_359",
          isTrust: "wallet_365",
          [["isMetaMask", "isOneInchAndroidWallet", "isOneInchIOSWallet"].toString()]:
            "wallet_361",
          [["isMathWallet", "isMetaMask"].toString()]: "wallet_370",
          [["isBitKeep", "isMetaMask"].toString()]: "wallet_371",
          [["isMetaMask", "isTokenPocket", "isTrust"].toString()]: "wallet_360",
          isPhantom: "wallet_433",
        })
      ),
      f = new Map(Object.entries({[a.ChainTypes.EVM]: () => window.ethereum})),
      getProviderByChainType = (e) => {
        const t = f.get(e.toString());
        if (void 0 !== t) return t();
      };
    t.getProviderByChainType = getProviderByChainType;
    t.getInstalledWalletPlugins = (e) => {
      const t = new Set(),
        n = e ? (0, s.default)(e) : a.ChainTypes.EVM,
        r = (0, i.default)().isMobile;
      r ||
        l.forEach((e) => {
          findProvider(e) && e.injectedProviderChainType === n && t.add(e.walletId);
        });
      const f = getProviderByChainType(n);
      if (f) {
        const e = null != f && f.providers ? f.providers : [f];
        for (const n of e) {
          const e = [];
          u.forEach((t) => {
            !0 === n[t] && e.push(t);
          });
          const i = r ? d.get(e.toString()) : c.get(e.toString());
          (i && t.has(i)) ||
            t.add(
              i || (r ? o.UnidentifiedMobileBrowserWallet : o.UnidentifiedPluginWallet)
            );
        }
      }
      return (
        t.size > 1 && t.delete("wallet_353"),
        t.size > 1 &&
          (t.delete(o.UnidentifiedMobileBrowserWallet),
          t.delete(o.UnidentifiedPluginWallet)),
        [...t]
      );
    };
    t.getEIP1193ProviderByWalletBrandId = (e) => {
      const t = l.filter((t) => t.brandId === e),
        n = (0, i.default)().isMobile;
      return 1 !== t.length || n
        ? window.ethereum
        : getEIP1193ProviderFromProviderPath(t[0]);
    };
    const getEIP1193ProviderFromProviderPath = (e) => {
        const t = window.ethereum;
        if (e.providerPath || t) {
          if (e.providerPath) {
            const t = findProvider(e);
            return t || void 0;
          }
          if (t) {
            const n = t.providers ? t.providers : [t];
            for (const t of n) {
              const n = [];
              u.forEach((e) => {
                !0 === t[e] && n.push(e);
              });
              if (c.get(n.toString()) === e.walletId) return t;
            }
          }
        }
      },
      findProvider = (e) => {
        var t;
        return null == e || null === (t = e.providerPath) || void 0 === t
          ? void 0
          : t.reduce((e, t) => {
              if (e) return e[t];
            }, window);
      };
  },
  4429: function (e, t, n) {
    e.exports = n(4430);
  },
  4430: function (e, t, n) {
    n(4431);
    var r = n(2794).Object;
    e.exports = function defineProperty(e, t, n) {
      return r.defineProperty(e, t, n);
    };
  },
  4431: function (e, t, n) {
    var r = n(3470);
    r(r.S + r.F * !n(2878), "Object", {defineProperty: n(2877).f});
  },
  4432: function (e, t, n) {
    var r = n(4433);
    e.exports = function (e, t, n) {
      if ((r(e), void 0 === t)) return e;
      switch (n) {
        case 1:
          return function (n) {
            return e.call(t, n);
          };
        case 2:
          return function (n, r) {
            return e.call(t, n, r);
          };
        case 3:
          return function (n, r, o) {
            return e.call(t, n, r, o);
          };
      }
      return function () {
        return e.apply(t, arguments);
      };
    };
  },
  4433: function (e, t) {
    e.exports = function (e) {
      if ("function" != typeof e) throw TypeError(e + " is not a function!");
      return e;
    };
  },
  4434: function (e, t, n) {
    var r = n(4308).default,
      o = n(4461);
    (e.exports = function _toPropertyKey(e) {
      var t = o(e, "string");
      return "symbol" === r(t) ? t : String(t);
    }),
      (e.exports.__esModule = !0),
      (e.exports.default = e.exports);
  },
  4435: function (e, t, n) {
    e.exports = n(4436);
  },
  4436: function (e, t, n) {
    n(4317), n(4448), n(4449), n(4450), (e.exports = n(2794).Symbol);
  },
  4437: function (e, t, n) {
    var r = n(3473)("meta"),
      o = n(3100),
      i = n(2879),
      a = n(2877).f,
      s = 0,
      u =
        Object.isExtensible ||
        function () {
          return !0;
        },
      c = !n(3099)(function () {
        return u(Object.preventExtensions({}));
      }),
      setMeta = function (e) {
        a(e, r, {value: {i: "O" + ++s, w: {}}});
      },
      l = (e.exports = {
        KEY: r,
        NEED: !1,
        fastKey: function (e, t) {
          if (!o(e))
            return "symbol" == typeof e ? e : ("string" == typeof e ? "S" : "P") + e;
          if (!i(e, r)) {
            if (!u(e)) return "F";
            if (!t) return "E";
            setMeta(e);
          }
          return e[r].i;
        },
        getWeak: function (e, t) {
          if (!i(e, r)) {
            if (!u(e)) return !0;
            if (!t) return !1;
            setMeta(e);
          }
          return e[r].w;
        },
        onFreeze: function (e) {
          return c && l.NEED && u(e) && !i(e, r) && setMeta(e), e;
        },
      });
  },
  4438: function (e, t, n) {
    var r = n(3477),
      o = n(4312),
      i = n(3537);
    e.exports = function (e) {
      var t = r(e),
        n = o.f;
      if (n)
        for (var a, s = n(e), u = i.f, c = 0; s.length > c; )
          u.call(e, (a = s[c++])) && t.push(a);
      return t;
    };
  },
  4439: function (e, t, n) {
    var r = n(4311);
    e.exports = Object("z").propertyIsEnumerable(0)
      ? Object
      : function (e) {
          return "String" == r(e) ? e.split("") : Object(e);
        };
  },
  4440: function (e, t, n) {
    var r = n(3076),
      o = n(4441),
      i = n(4442);
    e.exports = function (e) {
      return function (t, n, a) {
        var s,
          u = r(t),
          c = o(u.length),
          l = i(a, c);
        if (e && n != n) {
          for (; c > l; ) if ((s = u[l++]) != s) return !0;
        } else for (; c > l; l++) if ((e || l in u) && u[l] === n) return e || l || 0;
        return !e && -1;
      };
    };
  },
  4441: function (e, t, n) {
    var r = n(3534),
      o = Math.min;
    e.exports = function (e) {
      return e > 0 ? o(r(e), 9007199254740991) : 0;
    };
  },
  4442: function (e, t, n) {
    var r = n(3534),
      o = Math.max,
      i = Math.min;
    e.exports = function (e, t) {
      return (e = r(e)) < 0 ? o(e + t, 0) : i(e, t);
    };
  },
  4443: function (e, t, n) {
    var r = n(4311);
    e.exports =
      Array.isArray ||
      function isArray(e) {
        return "Array" == r(e);
      };
  },
  4444: function (e, t, n) {
    var r = n(2877),
      o = n(3471),
      i = n(3477);
    e.exports = n(2878)
      ? Object.defineProperties
      : function defineProperties(e, t) {
          o(e);
          for (var n, a = i(t), s = a.length, u = 0; s > u; )
            r.f(e, (n = a[u++]), t[n]);
          return e;
        };
  },
  4445: function (e, t, n) {
    var r = n(2793).document;
    e.exports = r && r.documentElement;
  },
  4446: function (e, t, n) {
    var r = n(3076),
      o = n(4314).f,
      i = {}.toString,
      a =
        "object" == typeof window && window && Object.getOwnPropertyNames
          ? Object.getOwnPropertyNames(window)
          : [];
    e.exports.f = function getOwnPropertyNames(e) {
      return a && "[object Window]" == i.call(e)
        ? (function (e) {
            try {
              return o(e);
            } catch (e) {
              return a.slice();
            }
          })(e)
        : o(r(e));
    };
  },
  4447: function (e, t, n) {
    var r = n(3537),
      o = n(3472),
      i = n(3076),
      a = n(3530),
      s = n(2879),
      u = n(4306),
      c = Object.getOwnPropertyDescriptor;
    t.f = n(2878)
      ? c
      : function getOwnPropertyDescriptor(e, t) {
          if (((e = i(e)), (t = a(t, !0)), u))
            try {
              return c(e, t);
            } catch (e) {}
          if (s(e, t)) return o(!r.f.call(e, t), e[t]);
        };
  },
  4448: function (e, t) {},
  4449: function (e, t, n) {
    n(3533)("asyncIterator");
  },
  4450: function (e, t, n) {
    n(3533)("observable");
  },
  4451: function (e, t, n) {
    e.exports = n(4452);
  },
  4452: function (e, t, n) {
    n(4453), n(4457), (e.exports = n(3475).f("iterator"));
  },
  4453: function (e, t, n) {
    "use strict";
    var r = n(4454)(!0);
    n(4315)(
      String,
      "String",
      function (e) {
        (this._t = String(e)), (this._i = 0);
      },
      function () {
        var e,
          t = this._t,
          n = this._i;
        return n >= t.length
          ? {value: void 0, done: !0}
          : ((e = r(t, n)), (this._i += e.length), {value: e, done: !1});
      }
    );
  },
  4454: function (e, t, n) {
    var r = n(3534),
      o = n(3529);
    e.exports = function (e) {
      return function (t, n) {
        var i,
          a,
          s = String(o(t)),
          u = r(n),
          c = s.length;
        return u < 0 || u >= c
          ? e
            ? ""
            : void 0
          : (i = s.charCodeAt(u)) < 55296 ||
              i > 56319 ||
              u + 1 === c ||
              (a = s.charCodeAt(u + 1)) < 56320 ||
              a > 57343
            ? e
              ? s.charAt(u)
              : i
            : e
              ? s.slice(u, u + 2)
              : a - 56320 + ((i - 55296) << 10) + 65536;
      };
    };
  },
  4455: function (e, t, n) {
    "use strict";
    var r = n(4313),
      o = n(3472),
      i = n(3532),
      a = {};
    n(3074)(a, n(3075)("iterator"), function () {
      return this;
    }),
      (e.exports = function (e, t, n) {
        (e.prototype = r(a, {next: o(1, n)})), i(e, t + " Iterator");
      });
  },
  4456: function (e, t, n) {
    var r = n(2879),
      o = n(3542),
      i = n(3535)("IE_PROTO"),
      a = Object.prototype;
    e.exports =
      Object.getPrototypeOf ||
      function (e) {
        return (
          (e = o(e)),
          r(e, i)
            ? e[i]
            : "function" == typeof e.constructor && e instanceof e.constructor
              ? e.constructor.prototype
              : e instanceof Object
                ? a
                : null
        );
      };
  },
  4457: function (e, t, n) {
    n(4458);
    for (
      var r = n(2793),
        o = n(3074),
        i = n(3538),
        a = n(3075)("toStringTag"),
        s =
          "CSSRuleList,CSSStyleDeclaration,CSSValueList,ClientRectList,DOMRectList,DOMStringList,DOMTokenList,DataTransferItemList,FileList,HTMLAllCollection,HTMLCollection,HTMLFormElement,HTMLSelectElement,MediaList,MimeTypeArray,NamedNodeMap,NodeList,PaintRequestList,Plugin,PluginArray,SVGLengthList,SVGNumberList,SVGPathSegList,SVGPointList,SVGStringList,SVGTransformList,SourceBufferList,StyleSheetList,TextTrackCueList,TextTrackList,TouchList".split(
            ","
          ),
        u = 0;
      u < s.length;
      u++
    ) {
      var c = s[u],
        l = r[c],
        d = l && l.prototype;
      d && !d[a] && o(d, a, c), (i[c] = i.Array);
    }
  },
  4458: function (e, t, n) {
    "use strict";
    var r = n(4459),
      o = n(4460),
      i = n(3538),
      a = n(3076);
    (e.exports = n(4315)(
      Array,
      "Array",
      function (e, t) {
        (this._t = a(e)), (this._i = 0), (this._k = t);
      },
      function () {
        var e = this._t,
          t = this._k,
          n = this._i++;
        return !e || n >= e.length
          ? ((this._t = void 0), o(1))
          : o(0, "keys" == t ? n : "values" == t ? e[n] : [n, e[n]]);
      },
      "values"
    )),
      (i.Arguments = i.Array),
      r("keys"),
      r("values"),
      r("entries");
  },
  4459: function (e, t) {
    e.exports = function () {};
  },
  4460: function (e, t) {
    e.exports = function (e, t) {
      return {value: t, done: !!e};
    };
  },
  4461: function (e, t, n) {
    var r = n(4462),
      o = n(4308).default;
    (e.exports = function _toPrimitive(e, t) {
      if ("object" !== o(e) || null === e) return e;
      var n = e[r];
      if (void 0 !== n) {
        var i = n.call(e, t || "default");
        if ("object" !== o(i)) return i;
        throw new TypeError("@@toPrimitive must return a primitive value.");
      }
      return ("string" === t ? String : Number)(e);
    }),
      (e.exports.__esModule = !0),
      (e.exports.default = e.exports);
  },
  4462: function (e, t, n) {
    e.exports = n(4463);
  },
  4463: function (e, t, n) {
    e.exports = n(3475).f("toPrimitive");
  },
  45: function (e, t, n) {
    "use strict";
    var r = n(21),
      o = n(84),
      i = r({}.hasOwnProperty);
    e.exports =
      Object.hasOwn ||
      function hasOwn(e, t) {
        return i(o(e), t);
      };
  },
  4522: function (e, t, n) {
    e.exports = n(4523);
  },
  4523: function (e, t, n) {
    "use strict";
    n(2), n(3);
    var r = n(2792);
    Object.defineProperty(t, "__esModule", {value: !0}),
      (t.default = t.Plaid = void 0),
      n(4524);
    var o = n(4392),
      i = _interopRequireWildcard(n(4529)),
      a = _interopRequireWildcard(n(4530)),
      s = _interopRequireWildcard(n(4531)),
      u = _interopRequireWildcard(n(4396)),
      c = n(3736),
      l = n(114),
      d = r(n(4532)),
      f = n(4535);
    function _getRequireWildcardCache(e) {
      if ("function" != typeof WeakMap) return null;
      var t = new WeakMap(),
        n = new WeakMap();
      return (_getRequireWildcardCache = function (e) {
        return e ? n : t;
      })(e);
    }
    function _interopRequireWildcard(e, t) {
      if (!t && e && e.__esModule) return e;
      if (null === e || ("object" != typeof e && "function" != typeof e))
        return {default: e};
      var n = _getRequireWildcardCache(t);
      if (n && n.has(e)) return n.get(e);
      var r = {},
        o = Object.defineProperty && Object.getOwnPropertyDescriptor;
      for (var i in e)
        if ("default" !== i && Object.prototype.hasOwnProperty.call(e, i)) {
          var a = o ? Object.getOwnPropertyDescriptor(e, i) : null;
          a && (a.get || a.set) ? Object.defineProperty(r, i, a) : (r[i] = e[i]);
        }
      return (r.default = e), n && n.set(e, r), r;
    }
    (u.messageHandlerExtensions[c.PLAID_INTERNAL_NAMESPACE] = []),
      u.messageHandlerExtensions[c.PLAID_INTERNAL_NAMESPACE].push(d.default),
      u.messageHandlerExtensions[c.PLAID_INTERNAL_NAMESPACE].push(
        i.extendMessageHandlers
      ),
      u.messageHandlerExtensions[c.PLAID_INTERNAL_NAMESPACE].push(
        s.extendMessageHandlers
      ),
      (u.messageHandlerExtensions[l.PLAID_FLOW_INTERNAL_NAMESPACE] = []),
      u.messageHandlerExtensions[l.PLAID_FLOW_INTERNAL_NAMESPACE].push(
        a.extendMessageHandlers
      );
    const p = {version: l.VERSION, create: o.create, createEmbedded: f.createEmbedded};
    (t.Plaid = p),
      void 0 !== window.Plaid &&
        console.warn(
          "Warning: The Plaid link-initialize.js script was embedded more than once. This is an unsupported configuration and may lead to unpredictable behavior. Please ensure Plaid Link is embedded only once per page."
        ),
      (window.Plaid = p);
    const v = i.findScriptTag();
    i.setUp(p, v), (e.exports = p);
    var _ = p;
    t.default = _;
  },
  4524: function (e, t, n) {
    "use strict";
    var r = n(114);
    n.p = r.LINK_CLIENT_URL + "/";
  },
  4525: function (e, t, n) {
    "use strict";
    var r = n(4);
    Object.defineProperty(t, "__esModule", {value: !0}),
      (t.create = void 0),
      n(69),
      n(2),
      n(3);
    var o = r(n(9)),
      i = _interopRequireWildcard(n(4393)),
      a = _interopRequireWildcard(n(4526)),
      s = _interopRequireWildcard(n(4527)),
      u = _interopRequireWildcard(n(4394)),
      c = _interopRequireWildcard(n(4395)),
      l = n(364),
      d = r(n(525)),
      f = r(n(638)),
      p = n(3734),
      v = n(4528);
    function _getRequireWildcardCache(e) {
      if ("function" != typeof WeakMap) return null;
      var t = new WeakMap(),
        n = new WeakMap();
      return (_getRequireWildcardCache = function (e) {
        return e ? n : t;
      })(e);
    }
    function _interopRequireWildcard(e, t) {
      if (!t && e && e.__esModule) return e;
      if (null === e || ("object" != typeof e && "function" != typeof e))
        return {default: e};
      var n = _getRequireWildcardCache(t);
      if (n && n.has(e)) return n.get(e);
      var r = {},
        o = Object.defineProperty && Object.getOwnPropertyDescriptor;
      for (var i in e)
        if ("default" !== i && Object.prototype.hasOwnProperty.call(e, i)) {
          var a = o ? Object.getOwnPropertyDescriptor(e, i) : null;
          a && (a.get || a.set) ? Object.defineProperty(r, i, a) : (r[i] = e[i]);
        }
      return (r.default = e), n && n.set(e, r), r;
    }
    function ownKeys(e, t) {
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
    function _objectSpread(e) {
      for (var t = 1; t < arguments.length; t++) {
        var n = null != arguments[t] ? arguments[t] : {};
        t % 2
          ? ownKeys(Object(n), !0).forEach(function (t) {
              (0, o.default)(e, t, n[t]);
            })
          : Object.getOwnPropertyDescriptors
            ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n))
            : ownKeys(Object(n)).forEach(function (t) {
                Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
              });
      }
      return e;
    }
    t.create = function (e) {
      let t = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : {};
      null != c.hooks.validateCreateOptions
        ? c.hooks.validateCreateOptions(e)
        : (0, v.validateCreateOptions)(e);
      let n = Date.now();
      const r = !0 === t.forceDesktop,
        o = !0 === t.forceMobile,
        _ = !0 === t.forcePopup,
        y = (!r && (0, d.default)().isMobile) || o,
        h = u.uuid(),
        g = (_ ? i : y ? s : a).create(),
        b = _objectSpread({}, e);
      delete b.onEvent, delete b.onExit, delete b.onLoad, delete b.onSuccess;
      const E = _objectSpread(
          {
            isMobile: y,
            uniqueId: h,
            linkOpenId: u.uuid(),
            origin: u.getWindowOrigin(),
            linkSdkVersion: l.LINK_WEB_SDK_VERSION,
            isLinkWebSdk: !0,
          },
          null == c.hooks.getConfig ? b : c.hooks.getConfig(e, t)
        ),
        m =
          null == c.hooks.getQueryParameters
            ? _objectSpread({}, E)
            : c.hooks.getQueryParameters(E);
      let w = u.buildLinkUrl(m),
        O = l.LINK_CLIENT_CORS_ORIGIN;
      null != c.hooks.updateLinkURL &&
        ((w = c.hooks.updateLinkURL(w, E)), (O = c.hooks.updateLinkURL(O, E)));
      const performOpen = (e) => {
          u.sendMessage(g, O)(_objectSpread({action: "open"}, e));
        },
        hideViewport = () => {
          (E.linkOpenId = u.uuid()), g.hide();
        },
        sendHeartBeat = () => {
          const {linkOpenId: e, env: t, token: n} = E;
          if (null != e && (null != t || null != n))
            try {
              const r = _objectSpread(
                _objectSpread({linkOpenId: e}, null != t && {env: t}),
                null != n && {token: n}
              );
              let o = u.buildLinkUrl(r, {
                LINK_CLIENT_STABLE_URL: l.LINK_CLIENT_STABLE_URL,
                LINK_CLIENT_URL: l.LINK_CLIENT_URL,
                LINK_HTML_PATH: l.LINK_OPEN_HTML_PATH,
              });
              null != c.hooks.updateLinkURL && (o = c.hooks.updateLinkURL(o, E)),
                null != c.hooks.emitLinkOpen
                  ? c.hooks.emitLinkOpen(o)
                  : (0, p.emitLinkOpen)(o);
            } catch (e) {}
          try {
            var r;
            const t = new XMLHttpRequest(),
              n = (0, f.default)(null !== (r = E.env) && void 0 !== r ? r : "");
            (t.onerror = () => {}),
              t.open("POST", n + "/link/heartbeat", !0),
              t.setRequestHeader("Content-Type", "application/json"),
              t.send(JSON.stringify({a: !0, b: !0, link_open_id: e}));
          } catch (e) {}
        };
      let S = null,
        I = 0;
      const P = {};
      P[l.PLAID_INTERNAL_NAMESPACE] = {
        exit: (t) => {
          "function" == typeof e.onExit && e.onExit(t.error, t.metadata),
            hideViewport(),
            (n = null);
        },
        event: (t) => {
          "function" == typeof e.onEvent && e.onEvent(t.eventName, t.metadata);
        },
        connected: (t) => {
          const n = t.metadata.link_session_id;
          S === n
            ? u.sendMessage(
                g,
                O
              )({action: "duplicate-handoff", msSinceFirstHandoff: Date.now() - I})
            : ((S = n), (I = Date.now())),
            e.onSuccess(t.metadata.public_token, t.metadata),
            hideViewport();
        },
        "ready-for-configure": () => {
          u.sendMessage(g, O)({action: "configure", config: E});
        },
        ready: () => {
          (A = !0),
            (N = null != n ? Date.now() - n : null),
            onReady(),
            "function" == typeof e.onLoad && e.onLoad();
        },
        resize: (e) => {
          null != e.height && null != g.resize && g.resize(e.height);
        },
      };
      for (const [n, r] of Object.entries(c.messageHandlerExtensions))
        r.forEach((r) => {
          P[n] = r(P[n] || {}, e, t, g);
        });
      const T = [];
      for (const [e, t] of Object.entries(P)) {
        const n = u.createMessageEventListener(
          e,
          h,
          t,
          g,
          w,
          u.createPostmessageMismatchReporter(g, O)
        );
        window.addEventListener("message", n, !1), T.push(n);
      }
      const exit = (t) => {
        if (g.isOpen()) {
          const n = {config: t};
          (0, v.validateExitOptions)(e, t),
            u.sendMessage(g, O)(_objectSpread({action: "exit"}, n));
        }
      };
      let L,
        x = !1,
        A = !1,
        onReady = () => {},
        N = null;
      g.initialize(w, h, t.isRenderedPreload);
      const open = function () {
          let e = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : null;
          if (x)
            throw new Error(
              "Cannot call open() on Link handler that is already destroyed"
            );
          const t = e || E.institution;
          e && L !== t
            ? ((E.institution = e || E.institution), (A = !1), g.refresh())
            : null != c.hooks.shouldReinitializeOnOpen &&
              c.hooks.shouldReinitializeOnOpen(E) &&
              ((A = !1), g.refresh()),
            (L = t),
            g.show(),
            sendHeartBeat();
          const r = Date.now(),
            o = null != n ? Date.now() - n : null;
          A
            ? performOpen({
                institution: e,
                openStartedAt: r,
                createToOnLoadInterval: N,
                createToOpenInterval: o,
                linkOpenId: E.linkOpenId,
              })
            : (onReady = () => {
                performOpen({
                  institution: e,
                  openStartedAt: r,
                  createToOnLoadInterval: N,
                  createToOpenInterval: o,
                  linkOpenId: E.linkOpenId,
                });
              });
        },
        submit = (e) => {
          const t = e;
          u.sendMessage(g, O)({action: "submit", data: t});
        },
        destroy = () => {
          (x = !0), g.destroy();
          for (const e of T) window.removeEventListener("message", e);
        };
      return {exit: exit, open: open, submit: submit, destroy: destroy};
    };
  },
  4526: function (e, t, n) {
    "use strict";
    Object.defineProperty(t, "__esModule", {value: !0}), (t.create = void 0);
    var r = n(364),
      o = n(3733);
    t.create = () => {
      let e,
        t = document.body.style.overflow,
        n = null,
        i = !1,
        a = null;
      const hide = () => {
        (i = !1),
          null != n && (n.style.display = "none"),
          "hidden" === document.body.style.overflow &&
            (document.body.style.overflow = t),
          window.parent.focus(),
          null != a && a.focus();
      };
      return {
        initialize: (t, i, a) => {
          (n = document.createElement("iframe")),
            (n.id = `plaid-link-iframe-${i}`),
            (n.title = "Plaid Link"),
            (n.src = t),
            (n.allow = r.LINK_IFRAME_ALLOW),
            n.setAttribute("sandbox", r.LINK_IFRAME_SANDBOX_PERMISSIONS),
            (n.width = "100%"),
            (n.height = "100%"),
            (0, o.setStyles)(n, o.FULL_SCREEN_STYLES),
            (n.style.colorScheme = "light"),
            (e = (0, o.renderedPreload)(n, a)),
            document.body.appendChild(n);
        },
        refresh: () => {
          null != n && (n.src += "");
        },
        show: () => {
          (i = !0),
            (t = document.body.style.overflow),
            (document.body.style.overflow = "hidden"),
            (a = document.activeElement),
            null != n &&
              (e && (e(), (e = void 0)),
              (n.style.display = "block"),
              null != n.contentWindow && n.contentWindow.focus());
        },
        hide: hide,
        postMessage: (e, t) => {
          null != n && null != n.contentWindow && n.contentWindow.postMessage(e, t);
        },
        isOpen: () => !0 === i,
        resize() {},
        destroy: () => {
          var e;
          (hide(), null != n) &&
            (null === (e = n.parentElement) || void 0 === e || e.removeChild(n),
            (n = null));
        },
        window: () => {
          var e, t;
          return null !==
            (e = null === (t = n) || void 0 === t ? void 0 : t.contentWindow) &&
            void 0 !== e
            ? e
            : null;
        },
      };
    };
  },
  4527: function (e, t, n) {
    "use strict";
    var r = n(4);
    Object.defineProperty(t, "__esModule", {value: !0}), (t.create = void 0);
    var o = n(364),
      i = n(3733),
      a = r(n(525));
    const s = "plaid-link-temporary-id",
      u = "plaid-link-iframe",
      c = "plaid-link-stylesheet",
      l = "html" + Array(9).join(`#${s}`),
      d = `\n  ${l},\n  ${l} > body {\n    overflow: hidden !important;\n  }\n  ${l} > body > .plaid-link-iframe {\n    display: flex !important;\n    position: fixed !important;\n    top: 0 !important;\n    left: 0 !important;\n    right: 0 !important;\n    bottom: 0 !important;\n    border: 0 !important;\n    overflow: auto !important;\n    height: 100% !important;\n    width: 100% !important;\n    z-index: 9999999999 !important;\n    background-color: rgba(17, 17, 18, 0.16) !important;\n  }\n`,
      f =
        "undefined" != typeof document
          ? (() => {
              try {
                var e;
                return (
                  (null === (e = document.currentScript) || void 0 === e
                    ? void 0
                    : e.nonce) || void 0
                );
              } catch (e) {
                return;
              }
            })()
          : void 0;
    t.create = () => {
      let e,
        t = null,
        n = !1,
        r = "",
        l = null,
        p = "",
        heightPriority = "",
        bodyHeight = "",
        bodyHeightPriority = "",
        resizeTimer = null,
        v = 0,
        _ = 0;
      const hide = () => {
        if (!n) return;
        if (resizeTimer !== null) {
          clearTimeout(resizeTimer);
          resizeTimer = null;
          document.body.style.setProperty("height", bodyHeight, bodyHeightPriority);
        }
        (n = !1),
          t && t.style.setProperty("display", "none", "important"),
          (() => {
            const e = document.getElementById(c);
            e && e.parentNode && e.parentNode.removeChild(e),
              r
                ? (document.documentElement.id = r)
                : document.documentElement.removeAttribute("id"),
              document.documentElement.style.setProperty("height", p, heightPriority),
              window.scrollTo(v, _),
              window.parent.focus(),
              null != l && l.focus();
          })();
      };
      return {
        refresh: () => {
          null != t && (t.src += "");
        },
        hide: hide,
        initialize: (n, r, a) => {
          (t = document.createElement("iframe")),
            (t.className = u),
            (t.title = "Plaid Link"),
            (t.id = `plaid-link-iframe-${r}`),
            (t.src = n),
            (t.allow = o.LINK_IFRAME_ALLOW),
            t.setAttribute("sandbox", o.LINK_IFRAME_SANDBOX_PERMISSIONS),
            t.style.setProperty("display", "none", "important"),
            (e = (0, i.renderedPreload)(
              t,
              a,
              Object.assign({width: "100%", height: "100%"}, i.FULL_SCREEN_STYLES)
            )),
            (t.style.colorScheme = "light"),
            document.body.appendChild(t);
        },
        isOpen: () => !0 === n,
        postMessage: (e, n) => {
          null != t && null != t.contentWindow && t.contentWindow.postMessage(e, n);
        },
        resize: (e) => {
          document.documentElement.style.setProperty("height", e, "important");
        },
        show: () => {
          if (
            !n &&
            ((n = !0),
            (l = document.activeElement),
            (v = window.scrollX),
            (_ = window.scrollY),
            (p = document.documentElement.style.height),
            (heightPriority = document.documentElement.style.getPropertyPriority("height")),
            (bodyHeight = document.body.style.getPropertyValue("height")),
            (bodyHeightPriority = document.body.style.getPropertyPriority("height")),
            (r = document.documentElement.id),
            (() => {
              const e = document.createElement("style");
              (e.id = c), f && (e.nonce = f), (e.textContent = d);
              const t = document.querySelector("head");
              null != t && t.appendChild(e);
            })(),
            (document.documentElement.id = s),
            t)
          ) {
            e && (e(), (e = void 0));
            const n = window.self !== window.top;
            (0, a.default)().isIOSChrome &&
              !n &&
              (resizeTimer = setTimeout(function () {
                document.body.style.setProperty(
                  "height",
                  window.innerHeight + "px",
                  "important"
                );
              }, 100)),
              t.style.setProperty("display", "block", "important"),
              t.focus(),
              t.contentWindow && t.contentWindow.focus();
          }
        },
        destroy: () => {
          var e;
          (hide(), null != t) &&
            (null === (e = t.parentElement) || void 0 === e || e.removeChild(t),
            (t = null));
        },
        window: () => {
          var e, n;
          return null !==
            (e = null === (n = t) || void 0 === n ? void 0 : n.contentWindow) &&
            void 0 !== e
            ? e
            : null;
        },
      };
    };
  },
  4528: function (e, t, n) {
    "use strict";
    Object.defineProperty(t, "__esModule", {value: !0}),
      (t.validateExitOptions = t.validateCreateOptions = void 0);
    var r = n(364);
    const getValidationHandlers = (e) => {
      let {env: t} = e;
      return {
        error: (e) => {
          if ("production" !== t) throw new Error(e);
        },
        warn: (e) => {
          "production" !== t && console.warn(e);
        },
      };
    };
    t.validateCreateOptions = (e) => {
      const {error: t} = getValidationHandlers(e);
      ((e) => {
        const {warn: t} = getValidationHandlers(e);
        for (const n in e)
          r.CREATE_PARAMETERS.indexOf(n) < 0 &&
            t(`Invalid Link parameter: ${n} is not a valid Plaid.create() parameter`);
      })(e),
        "function" != typeof e.onSuccess && t("Invalid onSuccess function"),
        null == e.receivedRedirectUri &&
          null == e.token &&
          t("Missing Link parameter. Link requires a token to be provided.");
    };
    t.validateExitOptions = (e, t) => {
      const {error: n} = getValidationHandlers(e);
      return (
        null == t ||
          ("object" != typeof t && n("Invalid exit parameter, must be an Object")),
        null
      );
    };
  },
  4529: function (e, t, n) {
    "use strict";
    var r = n(2792);
    Object.defineProperty(t, "__esModule", {value: !0}),
      (t.setUp = t.findScriptTag = t.extendMessageHandlers = void 0);
    var o = r(n(3073));
    n(13), n(98), n(99);
    var i = n(114);
    function ownKeys(e, t) {
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
    function _objectSpread(e) {
      for (var t = 1; t < arguments.length; t++) {
        var n = null != arguments[t] ? arguments[t] : {};
        t % 2
          ? ownKeys(Object(n), !0).forEach(function (t) {
              (0, o.default)(e, t, n[t]);
            })
          : Object.getOwnPropertyDescriptors
            ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n))
            : ownKeys(Object(n)).forEach(function (t) {
                Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
              });
      }
      return e;
    }
    t.findScriptTag = () => {
      const e = document.getElementsByTagName("script");
      if (e.length > 0) return e[0];
      throw new Error("Failed to find script");
    };
    t.extendMessageHandlers = (e, t, n, r) =>
      _objectSpread(
        _objectSpread({}, e),
        {},
        {
          acknowledged: () => {
            const e = document.getElementById(i.PLAID_LINK_BUTTON_ID);
            null != e && (e.disabled = !1);
          },
        }
      );
    const a = new RegExp(
        "public-([a-z]+)-[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}"
      ),
      traverse = (e, t) => {
        for (const n in e)
          "object" == typeof e[n]
            ? traverse(e[n], (e, r) => {
                t([n].concat(e), r);
              })
            : t([n], e[n]);
      };
    t.setUp = (e, t) => {
      const n = t.getAttribute("data-form-id");
      if (null == n) return;
      const r = document.getElementById(n);
      if (null == r) throw new Error("Uncaught Error: Specify a valid data-form-id");
      const o = t.getAttribute("data-api-version"),
        s = t.getAttribute("data-client-name"),
        u = t.getAttribute("data-product"),
        c = t.getAttribute("data-key"),
        l = t.getAttribute("data-env"),
        d = "true" === t.getAttribute("data-select-account"),
        f = t.getAttribute("data-token"),
        p = t.getAttribute("data-webhook"),
        v =
          null != t.getAttribute("data-longtail") ||
          null != t.getAttribute("data-long-tail") ||
          null,
        _ = e.create({
          apiVersion: o,
          clientName: s,
          env: l,
          isSimpleIntegration: !0,
          key: c,
          longtail: v,
          onSuccess: (e, t) => {
            traverse(t, (e, t) => {
              const n =
                e[0] +
                e
                  .slice(1)
                  .map((e) => `[${e}]`)
                  .join("");
              r.appendChild(
                ((e, t) => {
                  const n = document.createElement("input");
                  return (n.type = "hidden"), (n.name = e), (n.value = t), n;
                })(n, t)
              );
            }),
              r.submit();
          },
          product: u,
          selectAccount: d,
          token: f,
          webhook: p,
        }),
        y = document.createElement("button");
      (y.id = i.PLAID_LINK_BUTTON_ID),
        (y.textContent = ((e) => null != e && a.test(e))(f)
          ? "Link your bank account"
          : "Relink your bank account"),
        (y.onclick = (e) => {
          e.preventDefault(), _.open();
        }),
        r.appendChild(y);
    };
  },
  4530: function (e, t, n) {
    "use strict";
    var r = n(2792);
    Object.defineProperty(t, "__esModule", {value: !0}),
      (t.extendMessageHandlers = void 0);
    var o = r(n(3073));
    function ownKeys(e, t) {
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
    function _objectSpread(e) {
      for (var t = 1; t < arguments.length; t++) {
        var n = null != arguments[t] ? arguments[t] : {};
        t % 2
          ? ownKeys(Object(n), !0).forEach(function (t) {
              (0, o.default)(e, t, n[t]);
            })
          : Object.getOwnPropertyDescriptors
            ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n))
            : ownKeys(Object(n)).forEach(function (t) {
                Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
              });
      }
      return e;
    }
    t.extendMessageHandlers = (e, t, n, r) => {
      let o = !1;
      return _objectSpread(
        _objectSpread({}, e),
        {},
        {
          success: (e) => {
            (o = !0), "function" == typeof t.onSuccess && t.onSuccess("", e.metadata);
          },
          exit: (e) => {
            "function" != typeof t.onExit || o || t.onExit(e.error, e.metadata),
              r.hide();
          },
          event: (e) => {
            "function" == typeof t.onEvent && t.onEvent(e.event_name, e.metadata);
          },
        }
      );
    };
  },
  4531: function (e, t, n) {
    "use strict";
    var r = n(2792);
    Object.defineProperty(t, "__esModule", {value: !0}),
      (t.extendMessageHandlers = void 0);
    var o = r(n(3073));
    function ownKeys(e, t) {
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
    function _objectSpread(e) {
      for (var t = 1; t < arguments.length; t++) {
        var n = null != arguments[t] ? arguments[t] : {};
        t % 2
          ? ownKeys(Object(n), !0).forEach(function (t) {
              (0, o.default)(e, t, n[t]);
            })
          : Object.getOwnPropertyDescriptors
            ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n))
            : ownKeys(Object(n)).forEach(function (t) {
                Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
              });
      }
      return e;
    }
    t.extendMessageHandlers = (e, t, n, r) =>
      _objectSpread(
        _objectSpread({}, e),
        {},
        {
          result: (e) => {
            "function" == typeof t.onResult && t.onResult(e.incremental_result);
          },
        }
      );
  },
  4532: function (e, t, n) {
    "use strict";
    n(2), n(3);
    var r = n(2792);
    Object.defineProperty(t, "__esModule", {value: !0}), (t.default = void 0);
    var o = r(n(3073)),
      i = (function _interopRequireWildcard(e, t) {
        if (!t && e && e.__esModule) return e;
        if (null === e || ("object" != typeof e && "function" != typeof e))
          return {default: e};
        var n = _getRequireWildcardCache(t);
        if (n && n.has(e)) return n.get(e);
        var r = {},
          o = Object.defineProperty && Object.getOwnPropertyDescriptor;
        for (var i in e)
          if ("default" !== i && Object.prototype.hasOwnProperty.call(e, i)) {
            var a = o ? Object.getOwnPropertyDescriptor(e, i) : null;
            a && (a.get || a.set) ? Object.defineProperty(r, i, a) : (r[i] = e[i]);
          }
        (r.default = e), n && n.set(e, r);
        return r;
      })(n(3735)),
      a = n(279),
      s = r(n(4533)),
      u = r(n(4534)),
      c = n(114);
    function _getRequireWildcardCache(e) {
      if ("function" != typeof WeakMap) return null;
      var t = new WeakMap(),
        n = new WeakMap();
      return (_getRequireWildcardCache = function (e) {
        return e ? n : t;
      })(e);
    }
    function ownKeys(e, t) {
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
    function _objectSpread(e) {
      for (var t = 1; t < arguments.length; t++) {
        var n = null != arguments[t] ? arguments[t] : {};
        t % 2
          ? ownKeys(Object(n), !0).forEach(function (t) {
              (0, o.default)(e, t, n[t]);
            })
          : Object.getOwnPropertyDescriptors
            ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n))
            : ownKeys(Object(n)).forEach(function (t) {
                Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
              });
      }
      return e;
    }
    var _default = (e, t, n, r) => {
      const o = i.sendMessage(r),
        l = {chainId: c.MAINNET_HEX_CHAIN_ID, rpcUrl: c.CLOUDFLARE_ETH_MAINNET_URL};
      let d;
      return _objectSpread(
        _objectSpread({}, e),
        {},
        {
          connected: (t) => {
            const o = n.web3ConnectorCache;
            if (o) {
              const e = o.getConnector();
              if (!e) throw new Error("Unexpected state, missing connector");
              e.getProvider().then((e) => {
                if (!n.onProviderSuccess)
                  throw new Error("Unexpected state, missing onProviderSuccess");
                n.onProviderSuccess(e, t.metadata);
              }),
                r.hide();
            } else e.connected(t);
          },
          "web3-message": (e) => {
            d ||
              (d = (() => {
                if (n.web3Bridge) {
                  const e = n.web3Bridge;
                  return {then: (t) => t(e)};
                }
                return (0, s.default)().then((e) =>
                  (0, u.default)().then((t) => {
                    let {validateChainOptionAndChainInformation: n} = t;
                    return n(l), new e(l);
                  })
                );
              })()),
              d.then((t) => {
                t.setMessageSender(o),
                  (t.viewport = r),
                  e.message !== a.Web3MessageToTopWindow.START_BRIDGE &&
                    t.handleWeb3Message(e);
              });
          },
        }
      );
    };
    t.default = _default;
  },
  4533: function (e, t, n) {
    "use strict";
    n.r(t),
      (t.default = function () {
        return Promise.all([n.e(9), n.e(61), n.e(2), n.e(62)])
          .then(n.t.bind(null, 4792, 7))
          .then(function (e) {
            return e.Web3Bridge;
          });
      });
  },
  4534: function (e, t, n) {
    "use strict";
    n.r(t),
      (t.default = function () {
        return Promise.all([n.e(9), n.e(37)])
          .then(n.t.bind(null, 4791, 7))
          .then(function (e) {
            return {
              validateChainOptionAndChainInformation:
                e.validateChainOptionAndChainInformation,
            };
          });
      });
  },
  4535: function (e, t, n) {
    "use strict";
    var r = n(2792);
    Object.defineProperty(t, "__esModule", {value: !0}),
      (t.createEmbedded = void 0),
      n(69),
      n(2),
      n(3);
    var o = r(n(3073)),
      i = r(n(4536)),
      a = _interopRequireWildcard(n(3735)),
      s = n(114),
      u = n(4397),
      c = _interopRequireWildcard(n(4544)),
      l = n(364),
      d = n(3734),
      f = r(n(525)),
      p = n(4392),
      v = n(3736),
      _ = r(n(306)),
      y = n(4393);
    const h = ["embeddedComponentConfiguration"];
    function _getRequireWildcardCache(e) {
      if ("function" != typeof WeakMap) return null;
      var t = new WeakMap(),
        n = new WeakMap();
      return (_getRequireWildcardCache = function (e) {
        return e ? n : t;
      })(e);
    }
    function _interopRequireWildcard(e, t) {
      if (!t && e && e.__esModule) return e;
      if (null === e || ("object" != typeof e && "function" != typeof e))
        return {default: e};
      var n = _getRequireWildcardCache(t);
      if (n && n.has(e)) return n.get(e);
      var r = {},
        o = Object.defineProperty && Object.getOwnPropertyDescriptor;
      for (var i in e)
        if ("default" !== i && Object.prototype.hasOwnProperty.call(e, i)) {
          var a = o ? Object.getOwnPropertyDescriptor(e, i) : null;
          a && (a.get || a.set) ? Object.defineProperty(r, i, a) : (r[i] = e[i]);
        }
      return (r.default = e), n && n.set(e, r), r;
    }
    function ownKeys(e, t) {
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
    function _objectSpread(e) {
      for (var t = 1; t < arguments.length; t++) {
        var n = null != arguments[t] ? arguments[t] : {};
        t % 2
          ? ownKeys(Object(n), !0).forEach(function (t) {
              (0, o.default)(e, t, n[t]);
            })
          : Object.getOwnPropertyDescriptors
            ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n))
            : ownKeys(Object(n)).forEach(function (t) {
                Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
              });
      }
      return e;
    }
    t.createEmbedded = function (e, t) {
      let n = arguments.length > 2 && void 0 !== arguments[2] ? arguments[2] : {};
      const {embeddedComponentConfiguration: r} = e,
        o = (0, i.default)(e, h);
      (0, u.validateCreateOptions)(o);
      const g = `embedded_${a.uuid()}`,
        b = c.create(t),
        E = (0, u.validateEmbeddedComponentConfiguration)(r),
        m = _objectSpread(
          _objectSpread({}, o),
          {},
          {
            isEmbedded: !0,
            isEmbeddedLink: !0,
            isLinkInitialize: !0,
            isInIframe: a.isInIframe(),
            useMockFingerprint: n.useMockFingerprint,
            workflowVersionOverride: n.workflowVersionOverride,
          },
          !0 === n.forceDarkMode && {forceDarkMode: n.forceDarkMode}
        ),
        w = _objectSpread({}, m);
      delete w.onEvent, delete w.onExit, delete w.onLoad, delete w.onSuccess;
      const O = (0, f.default)().isMobile,
        S = _objectSpread(
          {
            isMobile: O,
            uniqueId: g,
            linkOpenId: (0, _.default)(),
            origin: a.getWindowOrigin(),
            linkSdkVersion: l.LINK_WEB_SDK_VERSION,
            isLinkWebSdk: !0,
          },
          w
        );
      let I,
        P = null;
      const getInternalOptionsForFullLink = () => {
          const e = {
            forceDarkMode: n.forceDarkMode,
            isEagerStart: n.isEagerStart,
            version: n.version,
            useMockFingerprint: n.useMockFingerprint,
            onProviderSuccess: n.onProviderSuccess,
          };
          return null != P && ((e.forceMobile = !0), (e.forcePopup = !0)), e;
        },
        T = {
          ready: () => {
            a.sendMessage(b)({action: "open"});
          },
          event: (e) => {
            "function" == typeof m.onEvent &&
              "HANDOFF" === e.eventName &&
              m.onEvent(e.eventName, e.metadata);
          },
          connected: (e) => {
            m.onSuccess(e.metadata.public_token, e.metadata);
          },
          "ready-for-configure": () => {
            a.sendMessage(b)({
              action: "configure",
              config:
                null != E ? _objectSpread({embeddedComponentConfiguration: E}, S) : S,
            });
          },
          "internal-event": (e) => {
            const t = e.event.start_link.link_token_configuration.institution_id;
            null == I && (I = (0, p.create)(o, getInternalOptionsForFullLink())),
              I.open(t);
          },
          "embedded-link-loaded": (e) => {
            null != I && I.destroy(),
              (I = (0, p.create)(
                o,
                _objectSpread(
                  _objectSpread({}, getInternalOptionsForFullLink()),
                  {},
                  {embeddedWorkflowSessionId: e.embedded_workflow_session_id}
                )
              ));
          },
          "preopen-popup-window": () => {
            try {
              P = (0, y.openLinkPopup)("");
            } catch (e) {
              P = null;
            }
          },
          "embedded-session-handoff": (e) => {
            null != I && I.destroy(),
              (I = (0, p.create)(
                o,
                _objectSpread(
                  _objectSpread({}, getInternalOptionsForFullLink()),
                  {},
                  {
                    continuationToken: e.continuation_token,
                    workflowSessionId: e.workflow_session_id,
                  }
                )
              )),
              I.open();
          },
          "embedded-link-resize": (e) => {
            const n = Number(e.height);
            !Number.isFinite(n) ||
              n <= 0 ||
              ((t.style.transition = "height 200ms ease"),
              (t.style.height = `${Math.ceil(n)}px`));
          },
        },
        L = _objectSpread(
          _objectSpread({}, S),
          {},
          {experimentVariants: JSON.stringify(o.experimentVariants), version: s.VERSION}
        ),
        x = a.buildLinkUrl(L, {
          LINK_CLIENT_URL: l.LINK_CLIENT_URL,
          LINK_CLIENT_STABLE_URL: l.LINK_CLIENT_STABLE_URL,
          LINK_HTML_PATH: l.EMBEDDED_LINK_HTML_PATH,
        }),
        A = [],
        N = a.createMessageEventListener(
          v.PLAID_INTERNAL_NAMESPACE,
          g,
          T,
          b,
          x,
          a.createPostmessageMismatchReporter(b)
        );
      window.addEventListener("message", N, !1), A.push(N);
      const destroy = () => {
          b.destroy();
          for (const e of A) window.removeEventListener("message", e);
          I && I.destroy(), null != P && P.close(), (P = null);
        },
        emitOpen = () => {
          const {linkOpenId: e, env: t, token: n} = S;
          if (null != e && (null != t || null != n))
            try {
              const r = _objectSpread(
                  _objectSpread({linkOpenId: e}, null != t && {env: t}),
                  null != n && {token: n}
                ),
                o = a.buildLinkUrl(r, {
                  LINK_CLIENT_STABLE_URL: l.LINK_CLIENT_STABLE_URL,
                  LINK_CLIENT_URL: l.LINK_CLIENT_URL,
                  LINK_HTML_PATH: l.LINK_OPEN_HTML_PATH,
                });
              (0, d.emitLinkOpen)(o);
            } catch (e) {}
        };
      return b.initialize(x, g), emitOpen(), {destroy: destroy};
    };
  },
  4536: function (e, t, n) {
    var r = n(4537),
      o = n(4539);
    (e.exports = function _objectWithoutProperties(e, t) {
      if (null == e) return {};
      var n,
        i,
        a = o(e, t);
      if (r) {
        var s = r(e);
        for (i = 0; i < s.length; i++)
          (n = s[i]),
            t.indexOf(n) >= 0 ||
              (Object.prototype.propertyIsEnumerable.call(e, n) && (a[n] = e[n]));
      }
      return a;
    }),
      (e.exports.__esModule = !0),
      (e.exports.default = e.exports);
  },
  4537: function (e, t, n) {
    e.exports = n(4538);
  },
  4538: function (e, t, n) {
    n(4317), (e.exports = n(2794).Object.getOwnPropertySymbols);
  },
  4539: function (e, t, n) {
    var r = n(4540);
    (e.exports = function _objectWithoutPropertiesLoose(e, t) {
      if (null == e) return {};
      var n,
        o,
        i = {},
        a = r(e);
      for (o = 0; o < a.length; o++) (n = a[o]), t.indexOf(n) >= 0 || (i[n] = e[n]);
      return i;
    }),
      (e.exports.__esModule = !0),
      (e.exports.default = e.exports);
  },
  4540: function (e, t, n) {
    e.exports = n(4541);
  },
  4541: function (e, t, n) {
    n(4542), (e.exports = n(2794).Object.keys);
  },
  4542: function (e, t, n) {
    var r = n(3542),
      o = n(3477);
    n(4543)("keys", function () {
      return function keys(e) {
        return o(r(e));
      };
    });
  },
  4543: function (e, t, n) {
    var r = n(3470),
      o = n(2794),
      i = n(3099);
    e.exports = function (e, t) {
      var n = (o.Object || {})[e] || Object[e],
        a = {};
      (a[e] = t(n)),
        r(
          r.S +
            r.F *
              i(function () {
                n(1);
              }),
          "Object",
          a
        );
    };
  },
  4544: function (e, t, n) {
    "use strict";
    Object.defineProperty(t, "__esModule", {value: !0}),
      (t.create = void 0),
      n(2),
      n(3);
    t.create = (e) => {
      let t = null;
      return {
        refresh: () => {
          null != t && (t.src += "");
        },
        initialize: (n, r) => {
          (t = document.createElement("iframe")),
            (t.id = `plaid-embedded-link-iframe-${r}`),
            (t.title = "Plaid Link"),
            (t.src = n),
            (t.width = "100%"),
            (t.height = "100%"),
            (t.style.borderWidth = "0"),
            e.replaceChildren(t);
        },
        show() {},
        hide() {},
        postMessage: (e, n) => {
          null != t && null != t.contentWindow && t.contentWindow.postMessage(e, n);
        },
        isOpen: () => !0,
        resize() {},
        destroy: () => {
          var e;
          null != t &&
            (null === (e = t.parentElement) || void 0 === e || e.removeChild(t),
            (t = null));
        },
        window: () => {
          var e, n;
          return null !==
            (e = null === (n = t) || void 0 === n ? void 0 : n.contentWindow) &&
            void 0 !== e
            ? e
            : null;
        },
      };
    };
  },
  470: function (e, t, n) {
    "use strict";
    var r = n(68),
      o = n(84),
      i = n(208),
      a = n(89),
      s = TypeError,
      u = "Reduce of empty array with no initial value",
      createMethod = function (e) {
        return function (t, n, c, l) {
          var d = o(t),
            f = i(d),
            p = a(d);
          if ((r(n), 0 === p && c < 2)) throw new s(u);
          var v = e ? p - 1 : 0,
            _ = e ? -1 : 1;
          if (c < 2)
            for (;;) {
              if (v in f) {
                (l = f[v]), (v += _);
                break;
              }
              if (((v += _), e ? v < 0 : p <= v)) throw new s(u);
            }
          for (; e ? v >= 0 : p > v; v += _) v in f && (l = n(l, f[v], v, d));
          return l;
        };
      };
    e.exports = {left: createMethod(!1), right: createMethod(!0)};
  },
  480: function (e, t, n) {
    "use strict";
    n(13);
    var r = n(28),
      o = n(76),
      i = n(254),
      a = n(22),
      s = n(27),
      u = n(107),
      c = s("species"),
      l = RegExp.prototype;
    e.exports = function (e, t, n, d) {
      var f = s(e),
        p = !a(function () {
          var t = {};
          return (
            (t[f] = function () {
              return 7;
            }),
            7 !== ""[e](t)
          );
        }),
        v =
          p &&
          !a(function () {
            var t = !1,
              n = /a/;
            return (
              "split" === e &&
                (((n = {}).constructor = {}),
                (n.constructor[c] = function () {
                  return n;
                }),
                (n.flags = ""),
                (n[f] = /./[f])),
              (n.exec = function () {
                return (t = !0), null;
              }),
              n[f](""),
              !t
            );
          });
      if (!p || !v || n) {
        var _ = /./[f],
          y = t(f, ""[e], function (e, t, n, o, a) {
            var s = t.exec;
            return s === i || s === l.exec
              ? p && !a
                ? {done: !0, value: r(_, t, n, o)}
                : {done: !0, value: r(e, n, t, o)}
              : {done: !1};
          });
        o(String.prototype, e, y[0]), o(l, f, y[1]);
      }
      d && u(l[f], "sham", !0);
    };
  },
  481: function (e, t, n) {
    "use strict";
    var r = n(270).charAt;
    e.exports = function (e, t, n) {
      return t + (n ? r(e, t).length || 1 : 1);
    };
  },
  482: function (e, t, n) {
    "use strict";
    var r = n(28),
      o = n(55),
      i = n(23),
      a = n(90),
      s = n(254),
      u = TypeError;
    e.exports = function (e, t) {
      var n = e.exec;
      if (i(n)) {
        var c = r(n, e, t);
        return null !== c && o(c), c;
      }
      if ("RegExp" === a(e)) return r(s, e, t);
      throw new u("RegExp#exec called on incompatible receiver");
    };
  },
  483: function (e, t, n) {
    "use strict";
    var r = n(51),
      o = n(90),
      i = n(27)("match");
    e.exports = function (e) {
      var t;
      return r(e) && (void 0 !== (t = e[i]) ? !!t : "RegExp" === o(e));
    };
  },
  485: function (e, t, n) {
    "use strict";
    var r = n(28),
      o = n(23),
      i = n(51),
      a = TypeError;
    e.exports = function (e, t) {
      var n, s;
      if ("string" === t && o((n = e.toString)) && !i((s = r(n, e)))) return s;
      if (o((n = e.valueOf)) && !i((s = r(n, e)))) return s;
      if ("string" !== t && o((n = e.toString)) && !i((s = r(n, e)))) return s;
      throw new a("Can't convert object to primitive value");
    };
  },
  486: function (e, t, n) {
    "use strict";
    var r = n(20),
      o = n(23),
      i = r.WeakMap;
    e.exports = o(i) && /native code/.test(String(i));
  },
  487: function (e, t, n) {
    "use strict";
    var r = n(101),
      o = n(21),
      i = n(293),
      a = n(343),
      s = n(55),
      u = o([].concat);
    e.exports =
      r("Reflect", "ownKeys") ||
      function ownKeys(e) {
        var t = i.f(s(e)),
          n = a.f;
        return n ? u(t, n(e)) : t;
      };
  },
  488: function (e, t, n) {
    "use strict";
    var r = Math.ceil,
      o = Math.floor;
    e.exports =
      Math.trunc ||
      function trunc(e) {
        var t = +e;
        return (t > 0 ? o : r)(t);
      };
  },
  489: function (e, t, n) {
    "use strict";
    var r = n(30),
      o = n(323),
      i = n(78),
      a = n(55),
      s = n(157),
      u = n(339);
    t.f =
      r && !o
        ? Object.defineProperties
        : function defineProperties(e, t) {
            a(e);
            for (var n, r = s(t), o = u(t), c = o.length, l = 0; c > l; )
              i.f(e, (n = o[l++]), r[n]);
            return e;
          };
  },
  490: function (e, t, n) {
    var r = n(327).default,
      o = n(491);
    (e.exports = function toPropertyKey(e) {
      var t = o(e, "string");
      return "symbol" == r(t) ? t : t + "";
    }),
      (e.exports.__esModule = !0),
      (e.exports.default = e.exports);
  },
  491: function (e, t, n) {
    var r = n(327).default;
    (e.exports = function toPrimitive(e, t) {
      if ("object" != r(e) || !e) return e;
      var n = e[Symbol.toPrimitive];
      if (void 0 !== n) {
        var o = n.call(e, t || "default");
        if ("object" != r(o)) return o;
        throw new TypeError("@@toPrimitive must return a primitive value.");
      }
      return ("string" === t ? String : Number)(e);
    }),
      (e.exports.__esModule = !0),
      (e.exports.default = e.exports);
  },
  492: function (e, t, n) {
    "use strict";
    var r = n(22);
    e.exports = !r(function () {
      function F() {}
      return (
        (F.prototype.constructor = null), Object.getPrototypeOf(new F()) !== F.prototype
      );
    });
  },
  493: function (e, t, n) {
    "use strict";
    var r = n(21),
      o = n(68);
    e.exports = function (e, t, n) {
      try {
        return r(o(Object.getOwnPropertyDescriptor(e, t)[n]));
      } catch (e) {}
    };
  },
  494: function (e, t, n) {
    "use strict";
    var r = n(495),
      o = String,
      i = TypeError;
    e.exports = function (e) {
      if (r(e)) return e;
      throw new i("Can't set " + o(e) + " as a prototype");
    };
  },
  495: function (e, t, n) {
    "use strict";
    var r = n(51);
    e.exports = function (e) {
      return r(e) || null === e;
    };
  },
  496: function (e, t, n) {
    "use strict";
    e.exports = {
      CSSRuleList: 0,
      CSSStyleDeclaration: 0,
      CSSValueList: 0,
      ClientRectList: 0,
      DOMRectList: 0,
      DOMStringList: 0,
      DOMTokenList: 1,
      DataTransferItemList: 0,
      FileList: 0,
      HTMLAllCollection: 0,
      HTMLCollection: 0,
      HTMLFormElement: 0,
      HTMLSelectElement: 0,
      MediaList: 0,
      MimeTypeArray: 0,
      NamedNodeMap: 0,
      NodeList: 1,
      PaintRequestList: 0,
      Plugin: 0,
      PluginArray: 0,
      SVGLengthList: 0,
      SVGNumberList: 0,
      SVGPathSegList: 0,
      SVGPointList: 0,
      SVGStringList: 0,
      SVGTransformList: 0,
      SourceBufferList: 0,
      StyleSheetList: 0,
      TextTrackCueList: 0,
      TextTrackList: 0,
      TouchList: 0,
    };
  },
  497: function (e, t, n) {
    "use strict";
    var r = n(198)("span").classList,
      o = r && r.constructor && r.constructor.prototype;
    e.exports = o === Object.prototype ? void 0 : o;
  },
  498: function (e, t, n) {
    "use strict";
    var r = n(21),
      o = n(84),
      i = Math.floor,
      a = r("".charAt),
      s = r("".replace),
      u = r("".slice),
      c = /\$([$&'`]|\d{1,2}|<[^>]*>)/g,
      l = /\$([$&'`]|\d{1,2})/g;
    e.exports = function (e, t, n, r, d, f) {
      var p = n + e.length,
        v = r.length,
        _ = l;
      return (
        void 0 !== d && ((d = o(d)), (_ = c)),
        s(f, _, function (o, s) {
          var c;
          switch (a(s, 0)) {
            case "$":
              return "$";
            case "&":
              return e;
            case "`":
              return u(t, 0, n);
            case "'":
              return u(t, p);
            case "<":
              c = d[u(s, 1, -1)];
              break;
            default:
              var l = +s;
              if (0 === l) return o;
              if (l > v) {
                var f = i(l / 10);
                return 0 === f
                  ? o
                  : f <= v
                    ? void 0 === r[f - 1]
                      ? a(s, 1)
                      : r[f - 1] + a(s, 1)
                    : o;
              }
              c = r[l - 1];
          }
          return void 0 === c ? "" : c;
        })
      );
    };
  },
  499: function (e, t, n) {
    "use strict";
    var r = n(21),
      o = n(320),
      i = n(23),
      a = n(90),
      s = n(80),
      u = r([].push);
    e.exports = function (e) {
      if (i(e)) return e;
      if (o(e)) {
        for (var t = e.length, n = [], r = 0; r < t; r++) {
          var c = e[r];
          "string" == typeof c
            ? u(n, c)
            : ("number" != typeof c && "Number" !== a(c) && "String" !== a(c)) ||
              u(n, s(c));
        }
        var l = n.length,
          d = !0;
        return function (e, t) {
          if (d) return (d = !1), t;
          if (o(this)) return t;
          for (var r = 0; r < l; r++) if (n[r] === e) return t;
        };
      }
    };
  },
  500: function (e, t, n) {
    "use strict";
    Object.defineProperty(t, "__esModule", {value: !0}),
      (t.TESTING_POSTMESSAGE_HOSTS = void 0);
    t.TESTING_POSTMESSAGE_HOSTS = [
      "secure-testing.plaid.com",
      "cdn-testing.plaid.com",
      "verify-qa.plaid.com",
      "verify-sandbox-qa.plaid.com",
      "verify-testing.plaid.com",
      "verify-testing.plaid.io",
      "flow-staging.cognitohq.com",
    ];
  },
  501: function (e, t, n) {
    "use strict";
    var r = n(28),
      o = n(45),
      i = n(121),
      a = n(318),
      s = RegExp.prototype;
    e.exports = function (e) {
      var t = e.flags;
      return void 0 !== t || "flags" in s || o(e, "flags") || !i(s, e) ? t : r(a, e);
    };
  },
  502: function (e, t, n) {
    "use strict";
    var r = n(78).f;
    e.exports = function (e, t, n) {
      n in e ||
        r(e, n, {
          configurable: !0,
          get: function () {
            return t[n];
          },
          set: function (e) {
            t[n] = e;
          },
        });
    };
  },
  51: function (e, t, n) {
    "use strict";
    var r = n(23);
    e.exports = function (e) {
      return "object" == typeof e ? null !== e : r(e);
    };
  },
  525: function (e, t, n) {
    "use strict";
    Object.defineProperty(t, "__esModule", {value: !0}), (t.default = void 0), n(13);
    t.default = () => {
      if (null == window.navigator) return {isIOSChrome: !1, isMobile: !1};
      const e = window.navigator,
        t = /windows phone/i.test(e.userAgent),
        n = /android|silk/i.test(e.userAgent) && !t,
        r = /iPad|iPhone|iPod/.test(e.userAgent) && !window.MSStream && !t;
      return {
        isIOSChrome: /CriOS/.test(e.userAgent),
        isMobile: r || n || t || /Mobi/i.test(e.userAgent),
      };
    };
  },
  55: function (e, t, n) {
    "use strict";
    var r = n(51),
      o = String,
      i = TypeError;
    e.exports = function (e) {
      if (r(e)) return e;
      throw new i(o(e) + " is not an object");
    };
  },
  552: function (e, t, n) {
    "use strict";
    var r = n(153),
      o = TypeError;
    e.exports = function (e, t) {
      if (!delete e[t]) throw new o("Cannot delete property " + r(t) + " of " + r(e));
    };
  },
  638: function (e, t, n) {
    "use strict";
    Object.defineProperty(t, "__esModule", {value: !0}), (t.default = void 0);
    var _default = (e) => {
      switch (e) {
        case "sandbox":
          return "https://sandbox.plaid.com";
        case "development":
          return "https://development.plaid.com";
        case "production":
          return "https://production.plaid.com";
        default:
          throw new Error(`Invalid environment: ${e}`);
      }
    };
    t.default = _default;
  },
  68: function (e, t, n) {
    "use strict";
    var r = n(23),
      o = n(153),
      i = TypeError;
    e.exports = function (e) {
      if (r(e)) return e;
      throw new i(o(e) + " is not a function");
    };
  },
  69: function (e, t, n) {
    "use strict";
    var r = n(29),
      o = n(101),
      i = n(267),
      a = n(28),
      s = n(21),
      u = n(22),
      c = n(23),
      l = n(216),
      d = n(185),
      f = n(499),
      p = n(247),
      v = String,
      _ = o("JSON", "stringify"),
      y = s(/./.exec),
      h = s("".charAt),
      g = s("".charCodeAt),
      b = s("".replace),
      E = s((1).toString),
      m = /[\uD800-\uDFFF]/g,
      w = /^[\uD800-\uDBFF]$/,
      O = /^[\uDC00-\uDFFF]$/,
      S =
        !p ||
        u(function () {
          var e = o("Symbol")("stringify detection");
          return "[null]" !== _([e]) || "{}" !== _({a: e}) || "{}" !== _(Object(e));
        }),
      I = u(function () {
        return '"\\udf06\\ud834"' !== _("\udf06\ud834") || '"\\udead"' !== _("\udead");
      }),
      stringifyWithSymbolsFix = function (e, t) {
        var n = d(arguments),
          r = f(t);
        if (c(r) || (void 0 !== e && !l(e)))
          return (
            (n[1] = function (e, t) {
              if ((c(r) && (t = a(r, this, v(e), t)), !l(t))) return t;
            }),
            i(_, null, n)
          );
      },
      fixIllFormed = function (e, t, n) {
        var r = h(n, t - 1),
          o = h(n, t + 1);
        return (y(w, e) && !y(O, o)) || (y(O, e) && !y(w, r))
          ? "\\u" + E(g(e, 0), 16)
          : e;
      };
    _ &&
      r(
        {target: "JSON", stat: !0, arity: 3, forced: S || I},
        {
          stringify: function stringify(e, t, n) {
            var r = d(arguments),
              o = i(S ? stringifyWithSymbolsFix : _, null, r);
            return I && "string" == typeof o ? b(o, m, fixIllFormed) : o;
          },
        }
      );
  },
  76: function (e, t, n) {
    "use strict";
    var r = n(23),
      o = n(78),
      i = n(324),
      a = n(250);
    e.exports = function (e, t, n, s) {
      s || (s = {});
      var u = s.enumerable,
        c = void 0 !== s.name ? s.name : t;
      if ((r(n) && i(n, c, s), s.global)) u ? (e[t] = n) : a(t, n);
      else {
        try {
          s.unsafe ? e[t] && (u = !0) : delete e[t];
        } catch (e) {}
        u
          ? (e[t] = n)
          : o.f(e, t, {
              value: n,
              enumerable: !1,
              configurable: !s.nonConfigurable,
              writable: !s.nonWritable,
            });
      }
      return e;
    };
  },
  78: function (e, t, n) {
    "use strict";
    var r = n(30),
      o = n(322),
      i = n(323),
      a = n(55),
      s = n(291),
      u = TypeError,
      c = Object.defineProperty,
      l = Object.getOwnPropertyDescriptor,
      d = "enumerable",
      f = "configurable",
      p = "writable";
    t.f = r
      ? i
        ? function defineProperty(e, t, n) {
            if (
              (a(e),
              (t = s(t)),
              a(n),
              "function" == typeof e &&
                "prototype" === t &&
                "value" in n &&
                p in n &&
                !n.writable)
            ) {
              var r = l(e, t);
              r &&
                r.writable &&
                ((e[t] = n.value),
                (n = {
                  configurable: f in n ? n.configurable : r.configurable,
                  enumerable: d in n ? n.enumerable : r.enumerable,
                  writable: !1,
                }));
            }
            return c(e, t, n);
          }
        : c
      : function defineProperty(e, t, n) {
          if ((a(e), (t = s(t)), a(n), o))
            try {
              return c(e, t, n);
            } catch (e) {}
          if ("get" in n || "set" in n) throw new u("Accessors not supported");
          return "value" in n && (e[t] = n.value), e;
        };
  },
  80: function (e, t, n) {
    "use strict";
    var r = n(139),
      o = String;
    e.exports = function (e) {
      if ("Symbol" === r(e))
        throw new TypeError("Cannot convert a Symbol value to a string");
      return o(e);
    };
  },
  81: function (e, t, n) {
    "use strict";
    var r,
      o,
      i,
      a = n(486),
      s = n(20),
      u = n(51),
      c = n(107),
      l = n(45),
      d = n(249),
      f = n(251),
      p = n(252),
      v = "Object already initialized",
      _ = s.TypeError,
      y = s.WeakMap;
    if (a || d.state) {
      var h = d.state || (d.state = new y());
      (h.get = h.get),
        (h.has = h.has),
        (h.set = h.set),
        (r = function (e, t) {
          if (h.has(e)) throw new _(v);
          return (t.facade = e), h.set(e, t), t;
        }),
        (o = function (e) {
          return h.get(e) || {};
        }),
        (i = function (e) {
          return h.has(e);
        });
    } else {
      var g = f("state");
      (p[g] = !0),
        (r = function (e, t) {
          if (l(e, g)) throw new _(v);
          return (t.facade = e), c(e, g, t), t;
        }),
        (o = function (e) {
          return l(e, g) ? e[g] : {};
        }),
        (i = function (e) {
          return l(e, g);
        });
    }
    e.exports = {
      set: r,
      get: o,
      has: i,
      enforce: function (e) {
        return i(e) ? o(e) : r(e, {});
      },
      getterFor: function (e) {
        return function (t) {
          var n;
          if (!u(t) || (n = o(t)).type !== e)
            throw new _("Incompatible receiver, " + e + " required");
          return n;
        };
      },
    };
  },
  84: function (e, t, n) {
    "use strict";
    var r = n(149),
      o = Object;
    e.exports = function (e) {
      return o(r(e));
    };
  },
  89: function (e, t, n) {
    "use strict";
    var r = n(229);
    e.exports = function (e) {
      return r(e.length);
    };
  },
  9: function (e, t, n) {
    var r = n(490);
    (e.exports = function _defineProperty(e, t, n) {
      return (
        (t = r(t)) in e
          ? Object.defineProperty(e, t, {
              value: n,
              enumerable: !0,
              configurable: !0,
              writable: !0,
            })
          : (e[t] = n),
        e
      );
    }),
      (e.exports.__esModule = !0),
      (e.exports.default = e.exports);
  },
  90: function (e, t, n) {
    "use strict";
    var r = n(21),
      o = r({}.toString),
      i = r("".slice);
    e.exports = function (e) {
      return i(o(e), 8, -1);
    };
  },
  92: function (e, t, n) {
    "use strict";
    e.exports = !1;
  },
  93: function (e, t, n) {
    "use strict";
    n(346);
  },
  96: function (e, t, n) {
    "use strict";
    var r = n(29),
      o = n(470).left,
      i = n(316),
      a = n(176);
    r(
      {
        target: "Array",
        proto: !0,
        forced: (!n(161) && a > 79 && a < 83) || !i("reduce"),
      },
      {
        reduce: function reduce(e) {
          var t = arguments.length;
          return o(this, e, t, t > 1 ? arguments[1] : void 0);
        },
      }
    );
  },
  98: function (e, t, n) {
    "use strict";
    var r = n(30),
      o = n(20),
      i = n(21),
      a = n(265),
      s = n(351),
      u = n(107),
      c = n(123),
      l = n(293).f,
      d = n(121),
      f = n(483),
      p = n(80),
      v = n(501),
      _ = n(319),
      y = n(502),
      h = n(76),
      g = n(22),
      b = n(45),
      E = n(81).enforce,
      m = n(297),
      w = n(27),
      O = n(255),
      S = n(326),
      I = w("match"),
      P = o.RegExp,
      T = P.prototype,
      L = o.SyntaxError,
      x = i(T.exec),
      A = i("".charAt),
      N = i("".replace),
      R = i("".indexOf),
      k = i("".slice),
      C = /^\?<[^\s\d!#%&*+<=>@^][^\s!#%&*+<=>@^]*>/,
      M = /a/g,
      j = /a/g,
      D = new P(M) !== M,
      U = _.MISSED_STICKY,
      W = _.UNSUPPORTED_Y,
      V =
        r &&
        (!D ||
          U ||
          O ||
          S ||
          g(function () {
            return (
              (j[I] = !1), P(M) !== M || P(j) === j || "/a/i" !== String(P(M, "i"))
            );
          }));
    if (a("RegExp", V)) {
      for (
        var K = function RegExp(e, t) {
            var n,
              r,
              o,
              i,
              a,
              l,
              _ = d(T, this),
              y = f(e),
              h = void 0 === t,
              g = [],
              m = e;
            if (!_ && y && h && e.constructor === K) return e;
            if (
              ((y || d(T, e)) && ((e = e.source), h && (t = v(m))),
              (e = void 0 === e ? "" : p(e)),
              (t = void 0 === t ? "" : p(t)),
              (m = e),
              O &&
                ("dotAll" in M) &&
                (r = !!t && R(t, "s") > -1) &&
                (t = N(t, /s/g, "")),
              (n = t),
              U &&
                ("sticky" in M) &&
                (o = !!t && R(t, "y") > -1) &&
                W &&
                (t = N(t, /y/g, "")),
              S &&
                ((i = (function (e) {
                  for (
                    var t,
                      n = e.length,
                      r = 0,
                      o = "",
                      i = [],
                      a = c(null),
                      s = !1,
                      u = !1,
                      l = 0,
                      d = "";
                    r <= n;
                    r++
                  ) {
                    if ("\\" === (t = A(e, r))) t += A(e, ++r);
                    else if ("]" === t) s = !1;
                    else if (!s)
                      switch (!0) {
                        case "[" === t:
                          s = !0;
                          break;
                        case "(" === t:
                          x(C, k(e, r + 1)) && ((r += 2), (u = !0)), (o += t), l++;
                          continue;
                        case ">" === t && u:
                          if ("" === d || b(a, d))
                            throw new L("Invalid capture group name");
                          (a[d] = !0), (i[i.length] = [d, l]), (u = !1), (d = "");
                          continue;
                      }
                    u ? (d += t) : (o += t);
                  }
                  return [o, i];
                })(e)),
                (e = i[0]),
                (g = i[1])),
              (a = s(P(e, t), _ ? this : T, K)),
              (r || o || g.length) &&
                ((l = E(a)),
                r &&
                  ((l.dotAll = !0),
                  (l.raw = K(
                    (function (e) {
                      for (var t, n = e.length, r = 0, o = "", i = !1; r <= n; r++)
                        "\\" !== (t = A(e, r))
                          ? i || "." !== t
                            ? ("[" === t ? (i = !0) : "]" === t && (i = !1), (o += t))
                            : (o += "[\\s\\S]")
                          : (o += t + A(e, ++r));
                      return o;
                    })(e),
                    n
                  ))),
                o && (l.sticky = !0),
                g.length && (l.groups = g)),
              e !== m)
            )
              try {
                u(a, "source", "" === m ? "(?:)" : m);
              } catch (e) {}
            return a;
          },
          H = l(P),
          B = 0;
        H.length > B;

      )
        y(K, P, H[B++]);
      (T.constructor = K), (K.prototype = T), h(o, "RegExp", K, {constructor: !0});
    }
    m("RegExp");
  },
  99: function (e, t, n) {
    "use strict";
    var r = n(30),
      o = n(255),
      i = n(90),
      a = n(135),
      s = n(81).get,
      u = RegExp.prototype,
      c = TypeError;
    r &&
      o &&
      a(u, "dotAll", {
        configurable: !0,
        get: function dotAll() {
          if (this !== u) {
            if ("RegExp" === i(this)) return !!s(this).dotAll;
            throw new c("Incompatible receiver, RegExp required");
          }
        },
      });
  },
});
