<html>
  <head>
    <title>{{title}}</title>
    <style>
      body {
      font-family: Courier;
      font-size: 12px;
      }
      p {
      margin: 20px;
      }
      a {
      text-decoration: none;
      font-weight: bold;
      }
      fieldset {
      padding: 1em;
      }
      label {
      float: left;
      margin-right: 0.5em;
      padding-top: 0.2em;
      text-align: right;
      font-weight: bold;
      }
      .note {
      font-size: x-small;
      }
    </style>
  </head>
  <body>
    <form method="post" action="/post">
      <fieldset>
        <legend>{{title}}</legend>
        <label for="upload">Contents: </label>
        <textarea id="upload" name="upload" rows="25"
                  cols="80">{{content}}</textarea>
        <br/>
        <label for="syntax">Force syntax: </label>
        <input id="syntax" name="syntax" value="{{syntax}}" />
        <br/>
        <label for="password">Password protect this paste (40char max):
        </label>
        <input id="password" type="password" name="password"
               maxlength="40" value="{{password}}" />
        <br/>
        <label for="is_encrypted">Is the password encrypted? </label>
        <input type="checkbox" name="is_encrypted" checked="{{checked}}"
               id="is_encrypted" />
        <br/>
        <input type="hidden" name="redirect" value="yes" />
        <input type="submit" value="Submit" />
      </fieldset>
      <p class="note">
        Keep in mind that passwords are transmitted in clear-text. The
        password is not cyphered on the client-side because shipping a
        SHA1 javascript library is perhaps too much, if you check the
        "Is encrypted?" checkbox make sure your password is cyphered
        with SHA1. Perhaps you better use the readily available
        <a
           href="https://raw.github.com/thekad/pasttle/master/pasttle.bashrc">
          console helper</a>?
      </p>
    </form>
  </body>
</html>
