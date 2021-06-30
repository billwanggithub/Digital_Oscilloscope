using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Windows.Forms.DataVisualization.Charting;
using Chart = System.Windows.Forms.DataVisualization.Charting.Chart;
using MY_UI;

namespace digital_oscillscope
{
    public partial class Form_waveform : Form
    {
        public object form_sender;
        public EventArgs form_e;

        public Form_waveform()
        {
            InitializeComponent();
        }

        private void Form_waveform_Load(object sender, EventArgs e)
        {

        }

        public void init_zoom(Chart chart)
        {
            if (!this.IsHandleCreated)
                return;

            chart.DisableZoomAndPanControls();
            chart.EnableZoomAndPanControls(ChartCursorSelected, ChartCursorMoved, zoomChanged, new ChartOption()
            {
                ContextMenuAllowToHideSeries = true,
                XAxisPrecision = 9,
                YAxisPrecision = 3,
                BufferedMode = true,
                DisplayDataSize = 800

                //XAxisPrecision = 4,
                //YAxisPrecision = 4
                //Theme = new DarkTheme(),
                //CursorLabelStringFormatX1 = "F0",
                //CursorLabelPrefixX1 = "X=",
                //CursorLabelPrefixY1 = "Y ",
                //CursorLabelPostfixY1 = "V"
            });
            // Client interface BUG:
            // OnAxisViewChang* is only called on Cursor_MouseUp, 
            //  so the following events are never raised
            chart.AxisViewChanging += OnAxisViewChanges;
            chart.AxisViewChanged += OnAxisViewChanges;
        }

        private void OnAxisViewChanges(object sender, ViewEventArgs viewEventArgs)
        {
            //Debug.Fail("Don't worry, this event is never raised.");
        }

        private void ChartCursorSelected(Chart sender, ChartCursor e)
        {
            if (!this.IsHandleCreated)
                return;

            this.InvokeOnUIThread(() =>
            {
                txtChartSelect.Text = "cursor=" + e.X.ToString("F9") + ", " + e.Y.ToString("F3");
                PointF diff = sender.CursorsDiff();
                txtCursorDelta.Text = "delta=" + diff.X.ToString("F9") + ", " + diff.Y.ToString("F3");
            });
        }

        private void ChartCursorMoved(Chart sender, ChartCursor e)
        {
            if (!this.IsHandleCreated)
                return;

            this.InvokeOnUIThread(() =>
            {
                txtChartValue.Text = "val=" + e.X.ToString("F9") + ", " + e.Y.ToString("F3");
            });
        }

        private void zoomChanged(Chart sender)
        {
        }

    }
}
