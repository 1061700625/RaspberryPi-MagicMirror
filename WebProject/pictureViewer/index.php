<!DOCTYPE html>
<?php
	function printFile($filepath)
	{ 
		if ( is_file ( $filepath))
		{
			$filename=iconv("gb2312","utf-8",$filepath);
			echo $filename."内容如下:"."<br/>";
			$fp = fopen ( $filepath, "r" );//打开文件
			#while (! feof ( $f )) //一直输出直到文件结尾
			$i = 1;
			while ($i < 10)
			{
				$line = fgets ( $fp );
				echo $line."<br/>";
				$i = $i +1;
			}
			fclose($fp);
		}	
	}
	
	function readFileRecursive($filepath)
	{
		if (is_dir ( $filepath )) //判断是不是目录
		{
			$dirhandle = opendir ( $filepath );//打开文件夹的句柄
			if ($dirhandle) 
			{
				//判断是不是有子文件或者文件夹
				while ( ($filename = readdir ( $dirhandle ))!= false ) 		
				{
					if ($filename == "." or $filename == "..")
					{
						//echo "目录为“.”或“..”"."<br/>";
						continue;
					}
					//判断是否为目录，如果为目录递归调用函数，否则直接读取打印文件
					if(is_dir ($filepath . "/" . $filename ))
					{
						readFileRecursive($filepath . "/" . $filename);
					}
					else
					{
						//打印文件
						printFile($filepath . "/" . $filename);
						echo "<br/>";
					}
				}
				closedir ( $dirhandle );
			}
		}
		else
		{
			printFile($filepath . "/" . $filename);
			return;
		}
	}

	function Scan_Files()
	{
		$hostdir=dirname(dirname(__FILE__))."/MagicMirror/images/";
		//获取本文件目录的文件夹地址
		 $filesnames = scandir($hostdir);
		//获取也就是扫描文件夹内的文件及文件夹名存入数组 $filesnames
		foreach ($filesnames as $name) 
		{
			if (is_dir($hostdir . $name) or $name == "." or $name == "..")
			{
				continue;
			}
			$url="images/".$name;
			$aurl= "<div class='cover'><img src='$url' alt=''></div>";
			echo $aurl;
		}
	}
?>

<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>pictureViewer</title>
    <link rel="stylesheet" href="./css/pictureViewer.css">
    <script src="js/pictureViewer.js"></script>
</head>
<body>
<div class="main-content">
    <h4 class="title">你笑起来真好看！</h4>
    <div class="image-list">
        <?php Scan_Files(); ?>
    </div>
</div>
<script src="http://www.jq22.com/jquery/jquery-1.10.2.js"></script>
<script src="./js/jquery.mousewheel.min.js"></script>
<script src="./js/pictureViewer.js"></script>
<script>
    $(function () {
        $('.image-list').on('click', '.cover', function () {
            var this_ = $(this);
            var images = this_.parents('.image-list').find('.cover');
            var imagesArr = new Array();
            $.each(images, function (i, image) {
                imagesArr.push($(image).children('img').attr('src'));
            });
            $.pictureViewer({
                images: imagesArr, //需要查看的图片，数据类型为数组
                initImageIndex: this_.index() + 1, //初始查看第几张图片，默认1
                scrollSwitch: true //是否使用鼠标滚轮切换图片，默认false
            });
        });
    });
</script>
</body>
</html>
