using VoltPy.Service;

var options = CommandLineOptions.Parse(args);
using var cts = new CancellationTokenSource();
Console.CancelKeyPress += (_, eventArgs) =>
{
    eventArgs.Cancel = true;
    cts.Cancel();
};

try
{
    var service = VoltPyService.Create(options);
    return options.Supervise
        ? await service.RunSupervisorAsync(options.AppName, TimeSpan.FromSeconds(5), cts.Token)
        : await service.RunOnceAsync(options.AppName, cts.Token);
}
catch (Exception ex)
{
    Console.Error.WriteLine(ex);
    return 1;
}
