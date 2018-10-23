# rest 路由设计

## 账户方向

    POST /account/login/ 登录

    POST /account/logout/ 登出

    POST /account/ 注册

    GET /account/<int:id>/ 获取账户信息

    PUT /account/<int:id>/ 更新账户信息（全部）

    PATCH /account/<int:id>/ 更新账户信息（部分）


### 管理员

    GET /account/list/<page> 获取账户id列表（默认100条，包含基本信息）

    GET /account/<int:id1>/<int:id2>/ 获取id1至id2之间的全部账户信息

    DELETE /account/<int:id>/ 删除账户