# rest 路由设计

## 账户方向

    POST /account/login/ 登录

    POST /account/logout/ 登出

    POST /account/user/ 注册

    GET /account/user/<int:id>/ 获取账户信息

    PUT /account/user/<int:id>/ 更新账户信息（全部）

    PATCH /account/user/<int:id>/ 更新账户信息（部分）

    POST /account/user/<int:id>/change-password/ 更改密码


### 管理员

    GET /account/id-list/?page=<int:page>&page_size=<int:page_size> 获取账户id列表（默认10条，包含基本信息）

    GET /account/detail/?id1=<int:id1>&id2=<int:id2>&page=<int:page>&page_size=<int:page_size> 获取id1至id2之间的全部账户信息

    DELETE /account/user/<int:id>/ 删除账户


## 部门

    GET /account/department/<int:id>/ 获取部门信息


### 管理员

    POST /account/department/ 添加部门

    PUT /account/department/<int:id>/ 更新部门信息（全部）

    PATCH /account/department/<int:id>/ 更新部门信息（部分）

    DELETE /account/department/<int:id>/ 删除部门