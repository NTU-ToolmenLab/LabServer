<%inherit file="root.mako"/>

<div class="container">
  <div class="row justify-content-center">
    <div class="col-5 login-container">
      <div class="form-login">
        <h4>Welcome to Lab304 !</h4>
        <form action="${action}" method="post">
      <input type="hidden" name="key" value="${key}"/>
      <input type="hidden" name="authn_reference" value="${authn_reference}"/>
      <input type="hidden" name="redirect_uri" value="${redirect_uri}"/>
          <input type="text"     name="userName"     placeholder="username"
                 class="form-control input-sm chat-input"/></br>
          <input type="password" name="userPassword" placeholder="password"
                 class="form-control input-sm chat-input"/></br>
          <div class="wrapper">
            <span class="group-btn">
          <input class="btn btn-primary btn-md" type="submit" name="form.submitted" value="Log In"/>
            </span>
          </div>
        </form>
      </div>
      % if error:
        <div class="alert alert-danger" role="alert">
          ${error}
        </div>
      % endif
    </div>
  </div>
</div>

<style>
@import url(http://fonts.googleapis.com/css?family=Roboto:400);
body {
  background-color:#fff;
  -webkit-font-smoothing: antialiased;
  font: normal 14px Roboto,arial,sans-serif;
}

.login-container {
  max-width: 35em;
  padding: 25px;
  position: fixed;
}

.form-login {
  background-color: #EDEDED;
  padding-top: 10px;
  padding-bottom: 20px;
  padding-left: 20px;
  padding-right: 20px;
  border-radius: 15px;
  border-color:#d2d2d2;
  border-width: 5px;
  box-shadow:0 1px 0 #cfcfcf;
}

h4 {
 border:0 solid #fff;
 border-bottom-width:1px;
 padding-bottom:10px;
 text-align: center;
}

.form-control {
  border-radius: 10px;
}

.wrapper {
  text-align: center;
}
</style>
