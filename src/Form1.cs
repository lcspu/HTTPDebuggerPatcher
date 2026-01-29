using System;
using System.Runtime.InteropServices;
using System.Text;
using System.Windows.Forms;
using Microsoft.Win32;
using System.Drawing;

namespace HttpDebuggerKeygen
{
    public partial class Form1 : Form
    {
        // P/Invoke for Volume Serial Number
        [DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        static extern bool GetVolumeInformation(string lpRootPathName, StringBuilder lpVolumeNameBuffer,
            int nVolumeNameSize, out uint lpVolumeSerialNumber, out uint lpMaximumComponentLength,
            out uint lpFileSystemFlags, StringBuilder lpFileSystemNameBuffer, int nFileSystemNameSize);

        private uint installedVersion = 0;

        public Form1()
        {
            InitializeComponent();
            this.Text = "Http Debugger 9.x Patcher";
            this.Size = new Size(360, 200);
            this.FormBorderStyle = FormBorderStyle.FixedSingle;
            this.MaximizeBox = false;
            this.Icon = Icon.ExtractAssociatedIcon(Application.ExecutablePath);

            SetupUI();
            installedVersion = GetHttpDebuggerVersion();
            lblVersionVal.Text = installedVersion.ToString();
        }

        private void SetupUI()
        {
            // Create a table with 1 column and 5 rows
            var table = new TableLayoutPanel
            {
                Dock = DockStyle.Fill,
                ColumnCount = 1,
                RowCount = 5,
                Padding = new Padding(10)
            };

            // Configure the column to center everything
            table.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100F));

            // 1. Installed Version Label
            var lblVerTitle = new Label
            {
                Text = "Installed Version",
                AutoSize = true,
                Anchor = AnchorStyles.None,
                Margin = new Padding(0, 5, 0, 0)
            };

            // 2. Version Value
            lblVersionVal = new Label
            {
                Text = "0",
                Font = new Font("Consolas", 10, FontStyle.Bold),
                AutoSize = true,
                Anchor = AnchorStyles.None
            };

            // 3. License Title
            var lblLicTitle = new Label
            {
                Text = "License Key",
                AutoSize = true,
                Anchor = AnchorStyles.None,
                Margin = new Padding(0, 15, 0, 0)
            };

            // 4. License Value Display
            lblLicense = new Label
            {
                Text = "*******",
                Font = new Font("Consolas", 10, FontStyle.Bold),
                Size = new Size(200, 30),
                TextAlign = ContentAlignment.MiddleCenter,
                Anchor = AnchorStyles.None
            };

            // 5. Make Button
            btnMake = new Button
            {
                Text = "Patch",
                Width = 100,
                Height = 35,
                Anchor = AnchorStyles.None,
                Margin = new Padding(0, 15, 0, 0)
            };
            btnMake.Click += BtnMake_Click;

            // Add controls to specific rows
            table.Controls.Add(lblVerTitle, 0, 0);
            table.Controls.Add(lblVersionVal, 0, 1);
            table.Controls.Add(lblLicTitle, 0, 2);
            table.Controls.Add(lblLicense, 0, 3);
            table.Controls.Add(btnMake, 0, 4);

            this.Controls.Add(table);
        }

        private Label lblVersionVal, lblLicense;
        private Button btnMake;

        private void BtnMake_Click(object sender, EventArgs e)
        {
            try
            {
                string regKeyName = CreateRegistryKeyName(installedVersion);
                string licKey = CreateLicenseKey();

                using (RegistryKey key = Registry.CurrentUser.CreateSubKey(@"Software\MadeForNet\HTTPDebuggerPro"))
                {
                    key.SetValue(regKeyName, licKey);
                }

                lblLicense.Text = licKey;
                MessageBox.Show("Registry patch success!", "Info", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message, "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        // --- Logic Core ---

        private uint GetHttpDebuggerVersion()
        {
            try
            {
                using (RegistryKey key = Registry.CurrentUser.OpenSubKey(@"Software\MadeForNet\HTTPDebuggerPro"))
                {
                    if (key == null) return 0;
                    string verFull = key.GetValue("AppVer")?.ToString() ?? "";
                    string verStr = verFull.Substring(verFull.LastIndexOf(' ') + 1).Replace(".", "");
                    return uint.TryParse(verStr, out uint v) ? v : 0;
                }
            }
            catch { return 0; }
        }

        private string CreateRegistryKeyName(uint version)
        {
            GetVolumeInformation("C:\\", null, 0, out uint serial, out _, out _, null, 0);
            uint notSerial = ~serial;
            uint calc = version ^ ((notSerial >> 1) + 736) ^ 0x590D4;
            return $"SN{calc}";
        }

        private string CreateLicenseKey()
        {
            Random rnd = new Random();
            byte r1 = (byte)rnd.Next(0, 255);
            byte r2 = (byte)rnd.Next(0, 255);
            byte r3 = (byte)rnd.Next(0, 255);

            return string.Format("{0:X2}{1:X2}{2:X2}7C{3:X2}{4:X2}{5:X2}{6:X2}",
                r1, (byte)(r2 ^ 0x7C), (byte)~r1, r2, r3, (byte)(r3 ^ 7), (byte)(r1 ^ (byte)~r3));
        }
    }
}