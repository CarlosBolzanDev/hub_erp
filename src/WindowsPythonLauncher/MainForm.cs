using System.Diagnostics;
using System.Text;
using System.Text.Json;

namespace WindowsPythonLauncher;

public sealed class MainForm : Form
{
    private readonly string _appRoot;
    private readonly string _scriptsDir;
    private readonly string _configDir;
    private readonly string _logsDir;
    private readonly string _settingsFile;
    private readonly string _selectedFile;
    private readonly JsonSerializerOptions _jsonOptions = new() { WriteIndented = true, PropertyNameCaseInsensitive = true };

    private readonly CheckedListBox _scriptList = new();
    private readonly Button _saveButton = new();
    private readonly Button _runButton = new();
    private readonly Button _reloadButton = new();
    private readonly TextBox _argsBox = new();
    private readonly RichTextBox _logBox = new();
    private readonly Label _statusLabel = new();

    private AppSettings _settings = new();
    private HashSet<string> _selectedScripts = new(StringComparer.OrdinalIgnoreCase);

    public MainForm()
    {
        Text = "Python Embedded Script Launcher";
        Width = 1040;
        Height = 680;
        MinimumSize = new Size(900, 560);
        StartPosition = FormStartPosition.CenterScreen;

        _appRoot = AppContext.BaseDirectory;
        _scriptsDir = Path.Combine(_appRoot, "Scripts");
        _configDir = Path.Combine(_appRoot, "config");
        _logsDir = Path.Combine(_appRoot, "logs");
        _settingsFile = Path.Combine(_configDir, "settings.json");
        _selectedFile = Path.Combine(_configDir, "selected_scripts.json");

        EnsureDirectories();
        LoadConfiguration();
        BuildUi();
        ReloadScripts();
    }

    private void BuildUi()
    {
        var root = new TableLayoutPanel
        {
            Dock = DockStyle.Fill,
            ColumnCount = 2,
            RowCount = 1,
            Padding = new Padding(14),
        };
        root.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 38));
        root.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 62));
        Controls.Add(root);

        var left = new TableLayoutPanel { Dock = DockStyle.Fill, RowCount = 6 };
        left.RowStyles.Add(new RowStyle(SizeType.AutoSize));
        left.RowStyles.Add(new RowStyle(SizeType.Percent, 100));
        left.RowStyles.Add(new RowStyle(SizeType.AutoSize));
        left.RowStyles.Add(new RowStyle(SizeType.AutoSize));
        left.RowStyles.Add(new RowStyle(SizeType.AutoSize));
        left.RowStyles.Add(new RowStyle(SizeType.AutoSize));
        root.Controls.Add(left, 0, 0);

        var title = new Label
        {
            Text = "Scripts disponíveis",
            Font = new Font(Font.FontFamily, 12, FontStyle.Bold),
            AutoSize = true,
            Margin = new Padding(0, 0, 0, 8),
        };
        left.Controls.Add(title, 0, 0);

        _scriptList.Dock = DockStyle.Fill;
        _scriptList.CheckOnClick = true;
        _scriptList.HorizontalScrollbar = true;
        left.Controls.Add(_scriptList, 0, 1);

        var argsLabel = new Label { Text = "Argumentos opcionais do script", AutoSize = true, Margin = new Padding(0, 12, 0, 4) };
        left.Controls.Add(argsLabel, 0, 2);

        _argsBox.Dock = DockStyle.Top;
        _argsBox.PlaceholderText = "Ex.: --cliente 123 --modo teste";
        left.Controls.Add(_argsBox, 0, 3);

        var buttons = new FlowLayoutPanel { Dock = DockStyle.Top, AutoSize = true, Margin = new Padding(0, 12, 0, 0) };
        _saveButton.Text = "Salvar seleção";
        _saveButton.AutoSize = true;
        _saveButton.Click += (_, _) => SaveSelection();
        buttons.Controls.Add(_saveButton);

        _runButton.Text = "Executar script";
        _runButton.AutoSize = true;
        _runButton.Click += async (_, _) => await RunSelectedScriptAsync();
        buttons.Controls.Add(_runButton);

        _reloadButton.Text = "Recarregar scripts";
        _reloadButton.AutoSize = true;
        _reloadButton.Click += (_, _) => ReloadScripts();
        buttons.Controls.Add(_reloadButton);
        left.Controls.Add(buttons, 0, 4);

        _statusLabel.Text = "Pronto";
        _statusLabel.AutoSize = true;
        _statusLabel.Margin = new Padding(0, 10, 0, 0);
        left.Controls.Add(_statusLabel, 0, 5);

        var right = new TableLayoutPanel { Dock = DockStyle.Fill, RowCount = 2, Padding = new Padding(12, 0, 0, 0) };
        right.RowStyles.Add(new RowStyle(SizeType.AutoSize));
        right.RowStyles.Add(new RowStyle(SizeType.Percent, 100));
        root.Controls.Add(right, 1, 0);

        var logTitle = new Label
        {
            Text = "Logs de execução",
            Font = new Font(Font.FontFamily, 12, FontStyle.Bold),
            AutoSize = true,
            Margin = new Padding(0, 0, 0, 8),
        };
        right.Controls.Add(logTitle, 0, 0);

        _logBox.Dock = DockStyle.Fill;
        _logBox.ReadOnly = true;
        _logBox.BackColor = Color.FromArgb(30, 30, 30);
        _logBox.ForeColor = Color.Gainsboro;
        _logBox.Font = new Font("Consolas", 10);
        right.Controls.Add(_logBox, 0, 1);
    }

    private void EnsureDirectories()
    {
        Directory.CreateDirectory(_scriptsDir);
        Directory.CreateDirectory(_configDir);
        Directory.CreateDirectory(_logsDir);
    }

    private void LoadConfiguration()
    {
        if (!File.Exists(_settingsFile))
        {
            _settings = new AppSettings();
            File.WriteAllText(_settingsFile, JsonSerializer.Serialize(_settings, _jsonOptions), Encoding.UTF8);
        }
        else
        {
            _settings = JsonSerializer.Deserialize<AppSettings>(File.ReadAllText(_settingsFile, Encoding.UTF8), _jsonOptions) ?? new AppSettings();
        }

        if (!File.Exists(_selectedFile))
        {
            File.WriteAllText(_selectedFile, JsonSerializer.Serialize(new SelectedScripts(), _jsonOptions), Encoding.UTF8);
        }

        var selected = JsonSerializer.Deserialize<SelectedScripts>(File.ReadAllText(_selectedFile, Encoding.UTF8), _jsonOptions) ?? new SelectedScripts();
        _selectedScripts = selected.Scripts.ToHashSet(StringComparer.OrdinalIgnoreCase);
    }

    private void ReloadScripts()
    {
        LoadConfiguration();
        _scriptList.Items.Clear();

        var scripts = Directory.GetFiles(_scriptsDir, "*.py", SearchOption.TopDirectoryOnly)
            .Select(Path.GetFileName)
            .Where(name => !string.IsNullOrWhiteSpace(name))
            .OrderBy(name => name, StringComparer.OrdinalIgnoreCase)
            .ToArray();

        foreach (var script in scripts)
        {
            _scriptList.Items.Add(script!, _selectedScripts.Contains(script!));
        }

        AppendLog($"Scripts recarregados: {scripts.Length} arquivo(s) encontrado(s).");
        SetStatus("Lista atualizada", Color.DarkBlue);
    }

    private void SaveSelection()
    {
        var selected = _scriptList.CheckedItems.Cast<string>().ToArray();
        var payload = new SelectedScripts { Scripts = selected };
        File.WriteAllText(_selectedFile, JsonSerializer.Serialize(payload, _jsonOptions), Encoding.UTF8);
        _selectedScripts = selected.ToHashSet(StringComparer.OrdinalIgnoreCase);
        AppendLog($"Seleção salva: {selected.Length} script(s).");
        SetStatus("Seleção salva", Color.DarkGreen);
    }

    private async Task RunSelectedScriptAsync()
    {
        if (_scriptList.SelectedItem is not string selectedScript)
        {
            SetStatus("Selecione um script na lista antes de executar", Color.DarkOrange);
            AppendLog("Nenhum script selecionado para execução.");
            return;
        }

        var scriptPath = Path.Combine(_scriptsDir, selectedScript);
        if (!File.Exists(scriptPath))
        {
            SetStatus("Arquivo de script não encontrado", Color.DarkRed);
            AppendLog($"ERRO: O arquivo não existe: {scriptPath}");
            return;
        }

        var pythonExe = Path.Combine(_appRoot, "engine", "python", "python.exe");
        var launcher = Path.Combine(_appRoot, "engine", "engine_launcher.py");
        if (!File.Exists(pythonExe))
        {
            SetStatus("Runtime Python embutido ausente", Color.DarkRed);
            AppendLog($"ERRO: Instale o Python embeddable package em: {Path.GetDirectoryName(pythonExe)}");
            return;
        }

        if (!File.Exists(launcher))
        {
            SetStatus("Launcher da engine ausente", Color.DarkRed);
            AppendLog($"ERRO: Arquivo da engine não encontrado: {launcher}");
            return;
        }

        SaveSelection();
        var contextFile = WriteRunContext(selectedScript, scriptPath);
        var logFile = Path.Combine(_logsDir, $"main-{DateTime.Now:yyyyMMdd}.log");
        var arguments = $"\"{launcher}\" --script \"{scriptPath}\" --context \"{contextFile}\" --log \"{logFile}\"";

        _runButton.Enabled = false;
        SetStatus($"Executando {selectedScript}...", Color.DarkBlue);
        AppendLog($"Iniciando script: {selectedScript}");

        try
        {
            var result = await Task.Run(() => RunProcess(pythonExe, arguments));
            AppendProcessOutput(result);

            if (result.ExitCode == 0)
            {
                SetStatus("Execução concluída com sucesso", Color.DarkGreen);
            }
            else
            {
                SetStatus($"Execução falhou (código {result.ExitCode})", Color.DarkRed);
            }
        }
        finally
        {
            _runButton.Enabled = true;
        }
    }

    private string WriteRunContext(string scriptName, string scriptPath)
    {
        var context = new
        {
            app_root = _appRoot,
            script_name = scriptName,
            script_path = scriptPath,
            scripts_dir = _scriptsDir,
            config_dir = _configDir,
            logs_dir = _logsDir,
            args = _argsBox.Text,
            settings = _settings,
            selected_scripts = _selectedScripts.OrderBy(x => x).ToArray(),
        };

        var path = Path.Combine(_configDir, "run_context.json");
        File.WriteAllText(path, JsonSerializer.Serialize(context, _jsonOptions), Encoding.UTF8);
        return path;
    }

    private ProcessResult RunProcess(string executable, string arguments)
    {
        var startInfo = new ProcessStartInfo
        {
            FileName = executable,
            Arguments = arguments,
            WorkingDirectory = _appRoot,
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            CreateNoWindow = true,
            StandardOutputEncoding = Encoding.UTF8,
            StandardErrorEncoding = Encoding.UTF8,
        };

        using var process = Process.Start(startInfo) ?? throw new InvalidOperationException("Não foi possível iniciar o processo Python.");
        var stdout = process.StandardOutput.ReadToEnd();
        var stderr = process.StandardError.ReadToEnd();
        process.WaitForExit();
        return new ProcessResult(process.ExitCode, stdout, stderr);
    }

    private void AppendProcessOutput(ProcessResult result)
    {
        if (!string.IsNullOrWhiteSpace(result.Stdout))
        {
            AppendLog(result.Stdout.Trim());
        }

        if (!string.IsNullOrWhiteSpace(result.Stderr))
        {
            AppendLog("STDERR:\n" + result.Stderr.Trim());
        }
    }

    private void AppendLog(string message)
    {
        var line = $"[{DateTime.Now:HH:mm:ss}] {message}{Environment.NewLine}";
        _logBox.AppendText(line);
        _logBox.ScrollToCaret();
        File.AppendAllText(Path.Combine(_logsDir, $"ui-{DateTime.Now:yyyyMMdd}.log"), line, Encoding.UTF8);
    }

    private void SetStatus(string text, Color color)
    {
        _statusLabel.Text = text;
        _statusLabel.ForeColor = color;
    }

    private sealed record ProcessResult(int ExitCode, string Stdout, string Stderr);

    private sealed class AppSettings
    {
        public string ScriptsFolder { get; set; } = "Scripts";
        public string EngineFolder { get; set; } = "engine";
        public bool WriteFileLogs { get; set; } = true;
    }

    private sealed class SelectedScripts
    {
        public string[] Scripts { get; set; } = Array.Empty<string>();
    }
}
