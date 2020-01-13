<!DOCTYPE html>
<html>
<head>
  <title>NGA Kanmusu Saimoe Monitor</title>
  <meta charset="utf-8">
  <link rel="icon" href="nga.ico">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <!-- Font Awesome -->
  <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.8.2/css/all.css">
  <!-- Bootstrap core CSS -->
  <link href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.3.1/css/bootstrap.min.css" rel="stylesheet">
  <!-- Material Design Bootstrap -->
  <link href="https://cdnjs.cloudflare.com/ajax/libs/mdbootstrap/4.10.1/css/mdb.min.css" rel="stylesheet">
  <!-- JQuery -->
  <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
  <!-- Bootstrap tooltips -->
  <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.4/umd/popper.min.js"></script>
  <!-- Bootstrap core JavaScript -->
  <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.3.1/js/bootstrap.min.js"></script>
  <!-- MDB core JavaScript -->
  <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/mdbootstrap/4.10.1/js/mdb.min.js"></script>
  <link rel="stylesheet" href="https://mladenplavsic.github.io/bootstrap-navbar-sidebar/navbar-fixed-left.min.css">
  <style type="text/css">a.btn{margin-bottom: 1rem;} hr{margin: 1rem;} .jumbotron{padding-bottom: 1rem}</style>
</head>
<body>
<nav class="navbar navbar-expand-md navbar-dark bg-primary fixed-left">
  <a class="navbar-brand" href="">NGA_SAIMOE</a>
  <button class="navbar-toggler collapsed" type="button" data-toggle="collapse" data-target="#navbarsExampleDefault" aria-controls="navbarsExampleDefault" aria-expanded="false" aria-label="Toggle navigation">
    <span class="navbar-toggler-icon"></span>
  </button>
  <div class="navbar-collapse collapse" id="navbarsExampleDefault" style="">
    <ul class="navbar-nav" id="sidebar">
    </ul>
  </div>
</nav>


<div class="container">
    <div class="jumbotron text-center">
      <h1>NGA舰萌 投票监控</h1>
      <p>人工验证 分词失败回帖内容记录表格</p>
    </div>
    <div class="table-responsive text-center">
      <table class="table col-sm w-auto table-striped table-borded table-hover" style="word-break:break-all; word-wrap:break-all;">
        <thead class="thead-dark">
        <tr>
          <th scope="col" class="th-sm">楼层</th>
          <th scope="col">回帖内容</th>
          <th scope="col">投票数</th>
          <th scope="col">分词数</th>
        </tr></thead>
        <tbody>
<?php
  $file=fopen("validation.log","r") or exit("Unable to open file!");
  while(!feof($file)){
    $line = fgets($file);
    if(strlen($line) < 2)
      continue;
    else if(strpos($line, "------>") !== false){
      $line = str_replace("------> output/", "", $line);
      $line = str_replace("-validation.csv\n", "", $line);
      echo "<tr><td></td><td><b id=\"" . $line . "\">" . $line . "</b></td><td></td><td></td><tr>";
    }
    else if(strpos($line, "超票") !== false){
      $line = str_replace("超票\t", "", $line);
      $line = str_replace("\t", "</td><td>", $line);
      echo "<tr><td>" . $line . "</td><td>超票</td></tr>";
    }
    else{
      $line = str_replace("\t", "</td><td>", $line);
      echo "<tr><td>" . $line . "</td></tr>";
    }
  }
  fclose($file);
?>      
        </tbody>
      </table>
    </div>
</div>

<script>
  window.onload = function() {
    groups = $('b');
    for ( i = 0; i < groups.length ; i ++){
      var gname = groups[i].id.split('-');
      $("#sidebar").append('<a class="nav-link" href="#' + groups[i].id + '">Group ' + gname[gname.length-1]+'</a>');
    }
  };
</script>
</body>
</html>