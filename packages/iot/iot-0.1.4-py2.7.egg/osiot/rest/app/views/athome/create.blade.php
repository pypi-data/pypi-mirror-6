
<!DOCTYPE html lang="zh-cn">
<html>
  	<head>
	    <meta http-equiv="Content-type" content="text/html; charset=utf-8">
	    <meta name="keywords" content="">
	    <meta name="viewport" content="width=device-width">
	    <meta name="description" content="">
	    <title>@yield('title')</title>
		<link rel="stylesheet" type="text/css" href="<?= url('css/bootstrap.min.css') ?>" />
		<link rel="stylesheet" type="text/css" href="<?= url('css/bootstrap-select.min.css') ?>" />
	</head>
<body>


<div class="container">

<div class="container">
  <div class="row-fluid">
<h1>Create </h1>

	{{ HTML::ul($errors->all()) }}
	{{ Form::open(array('url' => 'athome')) }}

       <div class="form-group">
			{{ Form::label('led1', '开关1') }}
			{{ Form::select('led1',array('关','开'),$selected=NULL,array('class'=>'selectpicker')) }}

		</div>

		<div class="form-group">
			{{ Form::label('sensors1', 'sensors1') }}
			{{ Form::text('sensors1', Input::old('sensors1'), array('class' => 'form-control')) }}
		</div>

		<div class="form-group">
			{{ Form::label('sensors2', 'sensors2') }}
			{{ Form::text('sensors2', Input::old('sensors2'), array('class' => 'form-control')) }}
		</div>

		<div class="form-group">
			{{ Form::label('temperature', 'temperature') }}
			{{ Form::text('temperature', Input::old('temperature'), array('class' => 'form-control')) }}
		</div>

		{{ Form::submit('Create!', array('class' => 'btn btn-primary')) }}

	{{ Form::close() }}

    </div>
</div>


<div class="footer">
        <p>&copy; Company 2013</p>
      </div>
</div>

</div>
<script type="text/javascript" src="<?= url('js/jquery.min.js')?>"></script>
<script type="text/javascript" src="<?= url('js/bootstrap.min.js') ?>"></script>
<script type="text/javascript" src="<?= url('js/bootstrap-select.min.js') ?>"></script>
<script>
 $('.selectpicker').selectpicker();
 </script>
<script type="text/javascript" src="<?= url('js/log.js') ?>"></script>


</body>
</html>