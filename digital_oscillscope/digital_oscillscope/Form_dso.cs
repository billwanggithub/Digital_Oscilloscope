using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Windows.Forms.DataVisualization.Charting;
using DSP;
using NWaves.Transforms;
using NWaves.Signals;
using DSO;
using MY_UI;
using MY_FUNCTION;

namespace digital_oscillscope
{
    public partial class Form_dso : Form
    {
        Form_waveform form_waveform = new Form_waveform();
        HDO4034A hdo4034a;

        Dictionary<string, ChartArea> chart_areas = new Dictionary<string, ChartArea>();
        Dictionary<string, Dictionary<string, (Series series, double[] x, double[] y)>> chart_series = new Dictionary<string, Dictionary<string, (Series series, double[] x, double[] y)>>();

        public Form_dso()
        {
            InitializeComponent();
        }

        private void button_test_Click(object sender, EventArgs e)
        {

        }

        private void button_read_scope_Click(object sender, EventArgs e)
        {

        }

        private void Form_dso_Load(object sender, EventArgs e)
        {
            form_waveform.Show();
        }

        private void button_clear_chart_Click(object sender, EventArgs e)
        {
            if (form_waveform.IsHandleCreated == false)
                return;
            clear_chart();
        }

        private void button_add_chart_Click(object sender, EventArgs e)
        {
            if (form_waveform.IsHandleCreated == false)
                return;
            add_chart(textBox_chartarea.Text, button_color_background.BackColor);
        }

        public void clear_chart()
        {
            object item_chart_area = comboBox_chart_area.SelectedItem;
            
            if (item_chart_area != null)
            {
                string chartarea_name = item_chart_area.ToString();

                ////// remove the combox item
                comboBox_chart_area.Items.Remove(item_chart_area);

                ////// enumerate all the series in the chartarea
                List<Series> series_list = new List<Series>();

                foreach( Series series in form_waveform.chart1.Series)
                {
                    if (series.Name.Contains(chartarea_name)) // check the chartarea name
                        series_list.Add(series);
                }

                ////// removes all series in the chararea
                foreach (Series series in series_list)
                {
                    form_waveform.chart1.Series.Remove(series);
                }

                ////// select the combox item
                if (comboBox_chart_area.Items.Count > 0)
                {
                    comboBox_chart_area.SelectedItem = comboBox_chart_area.Items[comboBox_chart_area.Items.Count - 1]; // select the last one
                }
                else
                {
                    comboBox_chart_area.Text = "";  // clear the text if no items
                }

                ////// remove the charterea in chart1 and all dictionarys
                form_waveform.chart1.ChartAreas.Remove(chart_areas[chartarea_name]);
                chart_areas.Remove(chartarea_name);
                chart_series.Remove(chartarea_name);
            }
            else
            {
                my_ui.console_print(richTextBox_console, $"Please Select a ChartArea\n", Color.Red);
            }
        }

        public void add_chart(string chartarea_name, Color color)
        {
            ////// Clear all chart areas in chart1
            //form_waveform.chart1.ChartAreas.Clear();
            //form_waveform.chart1.Series.Clear();

            ////// Create new chartarea and Add to chartareas list
            var new_chartarea = new ChartArea();
            new_chartarea.Name = chartarea_name;
            new_chartarea.AxisX.MajorGrid.LineColor = Color.LightGray;
            new_chartarea.AxisY.MajorGrid.LineColor = Color.LightGray;
            new_chartarea.AxisX.LabelStyle.Font = new Font("Consolas", 8);
            new_chartarea.AxisY.LabelStyle.Font = new Font("Consolas", 8);
            new_chartarea.BorderColor = Color.Black;
            new_chartarea.BorderWidth = 1;
            new_chartarea.BorderDashStyle = ChartDashStyle.Solid;
            new_chartarea.AxisX.LabelStyle.Format = "0.000000";
            new_chartarea.AxisY.LabelStyle.Format = "0.000";
            new_chartarea.BackColor = color;

            ////// add chararea to chart1 and dictionary
            if (chart_areas.ContainsKey(chartarea_name))
            {
                my_ui.console_print(richTextBox_console, $"ChartArea {chartarea_name} already exists!!\n", Color.Red);
                return;
            }
            form_waveform.chart1.ChartAreas.Add(new_chartarea);
            chart_areas.Add(new_chartarea.Name, form_waveform.chart1.ChartAreas[new_chartarea.Name]);
            chart_series.Add(new_chartarea.Name, new Dictionary<string, (Series series, double[] x, double[] y)>());

            ////// update combobox
            comboBox_chart_area.Items.Add(new_chartarea.Name);
            comboBox_chart_area.SelectedItem = new_chartarea.Name;

            // draw!
            form_waveform.chart1.Invalidate();
        }

        public bool read_waveform()
        {
            string ch_name = "";
            if (checkBox_read_from_file.Checked)
            {
                string fn = MyFile.get_open_file_name("Select Waveform", "All (*.trc)|*.trc");

                try
                {
                    hdo4034a = new HDO4034A();
                    hdo4034a.data["C1"].raw = File.ReadAllBytes(fn);
                    hdo4034a.parse_raw("C1");
                    DSO_DATA data_temp = hdo4034a.data["C1"];
                    hdo4034a.process_data(ref data_temp, null); ;
                    hdo4034a.data["C1"] = data_temp;
                }
                catch
                {
                    my_ui.console_printline(richTextBox_console, "File I/O Error!!");
                    return false;
                }
            }
            else
            {
                if (radioButton_ch1.Checked)
                    ch_name = "C1";
                else if (radioButton_ch2.Checked)
                    ch_name = "C2";
                else if (radioButton_ch3.Checked)
                    ch_name = "C3";
                else if (radioButton_ch4.Checked)
                    ch_name = "C4";
                else
                    return false;

                hdo4034a = new HDO4034A();
                hdo4034a.init();
                hdo4034a.read_raw(ch_name);
                hdo4034a.deinit();
                hdo4034a.parse_raw(ch_name);
                DSO_DATA data_temp = hdo4034a.data[ch_name];
                hdo4034a.process_data(ref data_temp, null);
                hdo4034a.data[ch_name] = data_temp;
            }

            return true;
        }

        public void test_charts()
        {
            //////// Clear all chart areas in chart1
            //form_waveform.chart1.ChartAreas.Clear();
            //form_waveform.chart1.Series.Clear();

            //////// Create new chartarea and Add to chartareas list
            //var chartArea = new ChartArea();
            //chartArea.Name = "chart_area" + chartareas.Count().ToString();
            ////chartArea.AxisX.LabelStyle.Format = "dd/MMM\nhh:mm";
            //chartArea.AxisX.MajorGrid.LineColor = Color.LightGray;
            //chartArea.AxisY.MajorGrid.LineColor = Color.LightGray;
            //chartArea.AxisX.LabelStyle.Font = new Font("Consolas", 8);
            //chartArea.AxisY.LabelStyle.Font = new Font("Consolas", 8);

            //chartareas.Add(chartArea);


            //////// Create new series and add to series list
            //string series_name = "series" + series.Count.ToString();
            //Series new_series = new Series(series_name)
            //{
            //    ChartType = SeriesChartType.Line,
            //    IsVisibleInLegend = true
            //};
            //new_series.ChartType = SeriesChartType.FastLine;
            //new_series.Points.AddXY(0, 0);
            //new_series.Points.AddXY(series.Count + 1, series.Count + 1);
            //series.Add(new_series);

            //// link series and chartarea
            //series1.ChartArea = "chartarea1";
            //series2.ChartArea = "chartarea2";


            ////// update charts
            //foreach (var (area, index) in chartareas.Select((area, index) => (area, index)))
            //{
            //    form_waveform.chart1.ChartAreas.Add(area);
            //    form_waveform.chart1.Series.Add(series[index]);

            //    //// link series and chartarea               
            //    form_waveform.chart1.Series[index].ChartArea = area.Name;

            //    // draw!
            //    form_waveform.chart1.Invalidate();
            //}
        }

        private void button_add_waveform_Click(object sender, EventArgs e)
        {
            add_series();
            enum_series();
        }

        public void add_series()
        {
            int len;
            double[] x = new double[] { 0, 1 };
            double[] y = new double[] { 0, 2 };
            double threshold_high;
            double threshold_low;
            string chart_area_name;
            string series_name;
            double x_begin, x_end, y_begin, y_end;
            int decimation_interval = 10;
            double cutoff_frequency = 0;
            int filter_order = 2;

            int x_begin_index = 0;
            int x_end_index = 0;

            ////// read waveform data
            if (read_waveform() == false)
                return;
            my_ui.console_print(richTextBox_console, $"Read Waveform OK!!\n");

            ////// Read parameters
            double gain = 1;
            double offset = 0;
            double.TryParse(textBox_gain.Text, out gain);
            double.TryParse(textBox_offset.Text, out offset);
            double.TryParse(textBox_threshold_pos.Text, out threshold_high);
            double.TryParse(textBox_threshold_negative.Text, out threshold_low);
            int.TryParse(textBox_decimation_interval.Text, out decimation_interval);
            double.TryParse(textBox_x_begin.Text, out x_begin);
            double.TryParse(textBox_x_end.Text, out x_end);
            double.TryParse(textBox_y_begin.Text, out y_begin);
            double.TryParse(textBox_y_end.Text, out y_end);
            double.TryParse(textBox_filter_cutoff.Text, out cutoff_frequency);
            int.TryParse(textBox_filter_order.Text, out filter_order);

            ////// Read Chartarea and series name
            object item_chart_area = comboBox_chart_area.SelectedItem;

            ////// If no chartarea created, create a new chartarea
            if (item_chart_area == null)
            {
                add_chart(textBox_chartarea.Text, button_color_background.BackColor);
                item_chart_area = comboBox_chart_area.SelectedItem;
            }
            chart_area_name = item_chart_area.ToString();
            series_name = chart_area_name + "," + textBox_waveform_name.Text.ToString();

            ////// Create new series 
            Series new_series = new Series(series_name)
            {
                ChartType = SeriesChartType.Line,
                IsVisibleInLegend = true
            };

            ////// Setting properity
            int line_size = 1;
            int.TryParse(textBox_line_size.Text, out line_size);

            if (radioButton_fastline.Checked)
            {
                new_series.ChartType = SeriesChartType.FastLine;
                new_series.BorderWidth = line_size;
            }
            else if (radioButton_point.Checked)
            {
                new_series.ChartType = SeriesChartType.Point;
                new_series.MarkerSize = line_size;
            }
            
            new_series.Color = button_color_line.BackColor;
            new_series.ChartArea = chart_area_name;
            if (radioButton_primary.Checked)
                new_series.YAxisType = AxisType.Primary;
            else if (radioButton_secondary.Checked)
                new_series.YAxisType = AxisType.Secondary;


            ////// Add series to chart1    
            bool is_series_exist = false;
            foreach (Series series in form_waveform.chart1.Series)
            {
                if (series.Name == series_name)
                {
                    is_series_exist = true;
                    break;
                }
            }

            ////// save data to dictionary
            if (is_series_exist)
            {
                form_waveform.chart1.Series.Remove(chart_series[chart_area_name][series_name].series);
                chart_series[chart_area_name].Remove(series_name);
            }

            form_waveform.chart1.Series.Add(series_name);
            form_waveform.chart1.Series[series_name] = new_series;
            chart_series[chart_area_name].Add(series_name, (form_waveform.chart1.Series[series_name], x, y));

            //////// read waveform data
            //read_waveform();

            ////// save data to dictionary
            
            string ch_name = "";
            if (checkBox_read_from_file.Checked)
                ch_name = "C1";
            else
            {
                if (radioButton_ch1.Checked)
                    ch_name = "C1";
                else if (radioButton_ch2.Checked)
                    ch_name = "C2";
                else if (radioButton_ch3.Checked)
                    ch_name = "C3";
                else if (radioButton_ch4.Checked)
                    ch_name = "C4";
            }

            if (ch_name == "")
            {
                return;
            }
            chart_series[chart_area_name][series_name] = (form_waveform.chart1.Series[series_name], hdo4034a.data[ch_name].x, hdo4034a.data[ch_name].y);


            var x_origonal = chart_series[chart_area_name][series_name].x;
            var y_origonal = chart_series[chart_area_name][series_name].y;
            var y_filtered = CLass_DSP.butterworth_filter(y_origonal, hdo4034a.data[ch_name].horizontal_interval, cutoff_frequency, filter_order);
            if ((radioButton_waveform.Checked) || (radioButton_frequency.Checked))
            {
                my_ui.console_print(richTextBox_console, $"Data Filter/Decimation\n");          

                my_ui.console_print(richTextBox_console, $"Data Filter/Decimation\n");
                //x = CLass_DSP.data_decimation(chart_series[chart_area_name][series_name].x, decimation_interval);
                //y = CLass_DSP.data_decimation(chart_series[chart_area_name][series_name].y, decimation_interval);

                double[] x_decimation;
                double[] y_decimation;

                (x_decimation, y_decimation) = CLass_DSP.moving_average(x_origonal, y_filtered, decimation_interval, 
                    false, progressBar1);

                int size_decimation = x_decimation.Count();
                if (size_decimation >= 2000000)
                {
                    DialogResult dialog_result = MessageBox.Show($"Display data count is {size_decimation / 1000000}M(over 2M)\nThis will cause memory overflow or time-consuming\n" +
                        "Please Reduce data count by decimation or zomm X axis\n Do you wang to continue",
                       "Display Count Warning!!", MessageBoxButtons.YesNo, MessageBoxIcon.Warning);
                    if (dialog_result == DialogResult.No)
                        return;
                }

                int power_of_2 = 0;
                if (radioButton_fft.Checked)
                {
                    for (power_of_2 = 0; power_of_2 < 25; power_of_2++)
                    {
                        if ((2 ^ power_of_2) >= size_decimation)
                        {
                            break;
                        }
                    }

                    double[] data_pof2 = new double[2 ^ power_of_2];
                    Array.Copy(y_decimation, data_pof2, y_decimation.Length);
                    var fft = new RealFft(2 ^ power_of_2);
                    //float[] spectrum = new float[2 ^ power_of_2];
                    int sampling_rate = (int)(1 / hdo4034a.data[ch_name].horizontal_interval);
                    var signal = new DiscreteSignal(sampling_rate, y_decimation.Select(v => (float)v).ToArray(), true);
                    var logPowerSpectrum =
                        fft.PowerSpectrum(signal)
                           .Samples
                           .Select(s => 20 * Math.Log10(s))
                           .ToArray();
                    (x, y) = (x_decimation, y_decimation);
                }
                else
                {
                    (x, y) = (x_decimation, y_decimation);
                }
            }
            else if (radioButton_duty.Checked)
            {
                my_ui.console_print(richTextBox_console, $"Calculating Duty cycles\n");
                var data_calculated = CLass_DSP.find_transitions(x_origonal, y_origonal, threshold_high, threshold_low, progressBar1);
                x = data_calculated.times_period.ToArray();
                y = data_calculated.dutys.ToArray();
            }
            else if (radioButton_frequency.Checked)
            {
                my_ui.console_print(richTextBox_console, $"Calculating Frequency\n");
                var data_calculated = CLass_DSP.find_transitions(x_origonal, y_origonal, threshold_high, threshold_low, progressBar1);
                x = data_calculated.times_period.ToArray();
                y = data_calculated.periods.Select(v => 1 / v).ToArray();
            }
            //////// scaling and offset
            my_ui.console_print(richTextBox_console, $"Scaling.....\n");
            y = y.Select(v => v * gain + offset).ToArray();


            if (x.Count() < 2)
            {
                return;
            }

            ////// calculate X begin/end index
            len = x.Count();
            if (checkBox_zoom_x.Checked)
            {
                x_begin_index = 0;
                x_end_index = len;
                for (int i = 0; i < len; i++)
                {
                    if (x[i] >= x_begin)
                    {
                        x_begin_index = i;
                        break;
                    }
                }

                for (int i = x_begin_index; i < len; i++)
                {
                    if (x[i] >= x_end)
                    {
                        x_end_index = i;
                        break;
                    }
                }
            }
            else
            {
                x_begin_index = 0;
                x_end_index = len - 1;
            }

            ////// copy zoom data to display buffer
            len = x_end_index - x_begin_index + 1;
            double[] x_zoom = new double[len];
            double[] y_zoom = new double[len];
            Array.Copy(x, x_begin_index, x_zoom, 0, len);
            Array.Copy(y, x_begin_index, y_zoom, 0, len);
            x_zoom = x_zoom.Select(v => Math.Round(v, 9)).ToArray();
            y_zoom = y_zoom.Select(v => Math.Round(v, 3)).ToArray();

            //chart_areas[chart_area_name].AxisX.Minimum = x_zoom.Min();
            //chart_areas[chart_area_name].AxisX.Maximum = x_zoom.Max();
            textBox_x_begin.Text = x_zoom.Min().ToString("0.000000000");
            textBox_x_end.Text = x_zoom.Max().ToString("0.000000000");

            if (checkBox_zoom_y.Checked)
            {
                chart_areas[chart_area_name].AxisY.Minimum = y_begin;
                chart_areas[chart_area_name].AxisY.Maximum = y_end;
            }
            else
            {
                if (x.Count() > 2)
                {
                    chart_areas[chart_area_name].AxisY.Minimum = y_zoom.Min();
                    chart_areas[chart_area_name].AxisY.Maximum = y_zoom.Max();
                    textBox_y_begin.Text = y_zoom.Min().ToString("0.000");
                    textBox_y_end.Text = y_zoom.Max().ToString("0.000");
                }
            }

            //// draw!
            my_ui.console_print(richTextBox_console, $"Plot Waveform... Please Wait!!!!\n");
            chart_series[chart_area_name][series_name].series.Points.Clear();
            //len = x_zoom.Length;
            //progressBar1.Maximum = len - 1;
            //for (int i =0; i < len; i++)
            //{
            //    chart_series[chart_area_name][series_name].series.Points.AddXY(x_zoom[i], y_zoom[i]);
            //    if ((i % 100000) == 0)
            //    {
            //        progressBar1.Value = i;
            //        Application.DoEvents();
            //        GC.Collect();
            //    }
            //}
            form_waveform.chart1.SuspendLayout();
            chart_series[chart_area_name][series_name].series.Points.DataBindXY(x_zoom, y_zoom);
            form_waveform.chart1.ResumeLayout();
            form_waveform.init_zoom(form_waveform.chart1);
            //form_waveform.chart1.Update();
            form_waveform.chart1.Invalidate();
            my_ui.console_print(richTextBox_console, $"Plot Waveform OK!!\n");
            GC.Collect();
        }

        public void plot_waveforms()
        {



            //form_waveform.chart1.ChartAreas.Add(area);
            //////// link series and chartarea               
            //form_waveform.chart1.Series[index].ChartArea = area.Name;


            //////// plot waveform
            //form_waveform.chart1.Series.Add(waveforms[chart_area_name][series_name]);

            ///////// draw!
            //form_waveform.chart1.Invalidate();
        }

        private void tabPage_main_Click(object sender, EventArgs e)
        {

        }

        private void button_color_Click(object sender, EventArgs e)
        {
            colorDialog1.ShowDialog();
            button_color_line.BackColor = colorDialog1.Color;
        }

        private void comboBox_series_MouseClick(object sender, MouseEventArgs e)
        {

            enum_series();
        }

        public void enum_series()
        {
            if (comboBox_chart_area.Items.Count > 0)
            {                
                string chartarea_name = comboBox_chart_area.SelectedItem.ToString();
                comboBox_series.Items.Clear();
                comboBox_series.Text = "";
                if (chartarea_name != null)
                {
                    ////// enumerate all the series in the chartarea
                    List<Series> series_list = new List<Series>();
                    foreach (Series series in form_waveform.chart1.Series)
                    {
                        if (series.Name.Contains(chartarea_name)) // check the chartarea name
                        {
                            comboBox_series.Items.Add(series.Name);
                            comboBox_series.SelectedItem = series.Name;
                        }
                    }
                }
            }
        }
        private void textBox_color_TextChanged(object sender, EventArgs e)
        {

        }

        private void button__clear_waveform_Click(object sender, EventArgs e)
        {

        }

        private void button_save_waveform_Click(object sender, EventArgs e)
        {
            string fn;
            string ch_name;
            if (radioButton_ch1.Checked)
                ch_name = "C1";
            else if (radioButton_ch2.Checked)
                ch_name = "C2";
            else if (radioButton_ch3.Checked)
                ch_name = "C3";
            else if (radioButton_ch4.Checked)
                ch_name = "C4";
            else
                return;

            hdo4034a = new HDO4034A();
            hdo4034a.init();
            if (hdo4034a.mb == null)
            {
                my_ui.console_print(richTextBox_console, $"DSO not found!!\n", Color.Red);
                return;
            }
 
            fn = MyFile.get_save_file_name("All (*.trc)|*.trc");
            if (fn == "")
            {
                return;
            }


            hdo4034a.read_raw(ch_name);
            hdo4034a.deinit();
            try
            {
                File.WriteAllBytes(fn, hdo4034a.data[ch_name].raw); // save to file
                my_ui.console_print(richTextBox_console, $"Save {ch_name} to {fn} OK!!\n", Color.Green);
            }
            catch
            {
                my_ui.console_print(richTextBox_console, $"File I/O error!!\n", Color.Red);
            }
            GC.Collect();
        }

        private void button_delete_waveform_Click(object sender, EventArgs e)
        {
            if (comboBox_series.Items.Count > 0)
            {
                object series_item = comboBox_series.SelectedItem;
                string series_name = series_item.ToString();
                string[] series_name_split = series_name.Split(new char[] { ',' });
                string chartarea_name = series_name_split[0];

                comboBox_series.Items.Remove(series_item);
                form_waveform.chart1.Series.Remove(chart_series[chartarea_name][series_name].series);
                chart_series[chartarea_name].Remove(series_name);
                enum_series();
            }
            else
            {
                my_ui.console_print(richTextBox_console, $"No waveforms to be deleted!!");
            }
            GC.Collect();
        }

        private void comboBox_series_SelectedIndexChanged(object sender, EventArgs e)
        {

        }

        private void radioButton_duty_CheckedChanged(object sender, EventArgs e)
        {
            check_waveform_type();
        }

        public void check_waveform_type()
        {
            if ((radioButton_duty.Checked) || (radioButton_frequency.Checked))
            {
                groupBox_threshold.Visible = true;
            }
            else
            {
                groupBox_threshold.Visible = false;
            }
        }

        private void radioButton_waveform_CheckedChanged(object sender, EventArgs e)
        {
            check_waveform_type();
        }

        private void radioButton_frequency_CheckedChanged(object sender, EventArgs e)
        {
            check_waveform_type();
        }

        private List<string> enum_chartaeea()
        {
            List<string> names = new List<string>();
            foreach(ChartArea chartarea in form_waveform.chart1.ChartAreas)
            {
                names.Add(chartarea.Name);
            }
            return names;
        }

        private void checkBox_x_alignment_CheckedChanged(object sender, EventArgs e)
        {
            List<string> chartareas_names = enum_chartaeea();
            if (checkBox_x_alignment.Checked)
            {
                if (chartareas_names.Count > 1)
                {
                    string first_chartarea_name = chartareas_names.First();
                    chartareas_names.Remove(first_chartarea_name);
                    foreach (string name in chartareas_names)
                    {
                        form_waveform.chart1.ChartAreas[name].AlignWithChartArea = first_chartarea_name; //or "ChartArea1"
                                                                                                         // Set the alignment type
                        form_waveform.chart1.ChartAreas[name].AlignmentStyle = AreaAlignmentStyles.Position |
                                                                        AreaAlignmentStyles.PlotPosition |
                                                                        AreaAlignmentStyles.Cursor |
                                                                        AreaAlignmentStyles.AxesView;
                    }
                }
            }
            else
            {
                if (chartareas_names.Count > 1)
                {
                    foreach (string name in chartareas_names)
                    {
                        form_waveform.chart1.ChartAreas[name].AlignWithChartArea = "";
                    }
                }
            }
        }

        private void button_color_background_Click(object sender, EventArgs e)
        {
            colorDialog1.ShowDialog();
            button_color_background.BackColor = colorDialog1.Color;
        }

        private void radioButton_fft_CheckedChanged(object sender, EventArgs e)
        {
            check_waveform_type();
        }
    }
}
