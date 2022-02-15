<?php
	header("content-type:text/html;charset=utf-8"); //设置编码

	if ($_FILES["file"]["error"] > 0)
  	{
  		echo "error";
  	}
	else
	{
		if (file_exists("images/" . $_FILES["file"]["name"]))
      	{
      		echo "exist";
      	}
    	else
      	{
			$newPath = "images/" . $_FILES["file"]["name"];
      		move_uploaded_file($_FILES["file"]["tmp_name"] , $newPath);
      		echo "ok";
      	}
	}
?>
