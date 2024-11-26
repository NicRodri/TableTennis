extern "C" void draw_detections_cv_v3(mat_cv* mat, detection *dets, int num, float thresh, char **names, image **alphabet, int classes, int ext_output)
{
    try {
        cv::Mat *show_img = (cv::Mat*)mat;
        int i, j;
        if (!show_img) return;
        static int frame_id = 0;
        frame_id++;

        // Static variables to track scores
        static int score_player1 = 0; // Player on the left
        static int score_player2 = 0; // Player on the right

        for (i = 0; i < num; ++i) {
            char labelstr[4096] = { 0 };
            int class_id = -1;
            for (j = 0; j < classes; ++j) {
                int show = strncmp(names[j], "dont_show", 9);
                if (dets[i].prob[j] > thresh && show) {
                    if (class_id < 0) {
                        strcat(labelstr, names[j]);
                        class_id = j;
                        char buff[20];
                        if (dets[i].track_id) {
                            sprintf(buff, " (id: %d)", dets[i].track_id);
                            strcat(labelstr, buff);
                        }
                        sprintf(buff, " (%2.0f%%)", dets[i].prob[j] * 100);
                        strcat(labelstr, buff);
                        printf("%s: %.0f%% ", names[j], dets[i].prob[j] * 100);
                        if (dets[i].track_id) printf("(track = %d, sim = %f) ", dets[i].track_id, dets[i].sim);
                    }
                    else {
                        strcat(labelstr, ", ");
                        strcat(labelstr, names[j]);
                        printf(", %s: %.0f%% ", names[j], dets[i].prob[j] * 100);
                    }
                }
            }
            if (class_id >= 0) {
                int width = std::max(1.0f, show_img->rows * .002f);

                int offset = class_id * 123457 % classes;
                float red = get_color(2, offset, classes);
                float green = get_color(1, offset, classes);
                float blue = get_color(0, offset, classes);
                float rgb[3];

                rgb[0] = red;
                rgb[1] = green;
                rgb[2] = blue;
                box b = dets[i].bbox;
                if (std::isnan(b.w) || std::isinf(b.w)) b.w = 0.5;
                if (std::isnan(b.h) || std::isinf(b.h)) b.h = 0.5;
                if (std::isnan(b.x) || std::isinf(b.x)) b.x = 0.5;
                if (std::isnan(b.y) || std::isinf(b.y)) b.y = 0.5;
                b.w = (b.w < 1) ? b.w : 1;
                b.h = (b.h < 1) ? b.h : 1;
                b.x = (b.x < 1) ? b.x : 1;
                b.y = (b.y < 1) ? b.y : 1;

                int left = (b.x - b.w / 2.)*show_img->cols;
                int right = (b.x + b.w / 2.)*show_img->cols;
                int top = (b.y - b.h / 2.)*show_img->rows;
                int bot = (b.y + b.h / 2.)*show_img->rows;

                if (left < 0) left = 0;
                if (right > show_img->cols - 1) right = show_img->cols - 1;
                if (top < 0) top = 0;
                if (bot > show_img->rows - 1) bot = show_img->rows - 1;

                // Scoring logic: Check if the ball crosses the edges
                if (left <= 0) {
                    score_player2++; // Ball crossed the left edge, Player 2 scores
                } else if (right >= show_img->cols) {
                    score_player1++; // Ball crossed the right edge, Player 1 scores
                }

                float const font_size = show_img->rows / 1000.F;
                cv::Size const text_size = cv::getTextSize(labelstr, cv::FONT_HERSHEY_COMPLEX_SMALL, font_size, 1, 0);
                cv::Point pt1, pt2, pt_text, pt_text_bg1, pt_text_bg2;
                pt1.x = left;
                pt1.y = top;
                pt2.x = right;
                pt2.y = bot;
                pt_text.x = left;
                pt_text.y = top - 4;
                pt_text_bg1.x = left;
                pt_text_bg1.y = top - (3 + 18 * font_size);
                pt_text_bg2.x = right;
                if ((right - left) < text_size.width) pt_text_bg2.x = left + text_size.width;
                pt_text_bg2.y = top;

                cv::Scalar color;
                color.val[0] = red * 256;
                color.val[1] = green * 256;
                color.val[2] = blue * 256;

                cv::rectangle(*show_img, pt1, pt2, color, width, 8, 0);

                cv::rectangle(*show_img, pt_text_bg1, pt_text_bg2, color, width, 8, 0);
                cv::rectangle(*show_img, pt_text_bg1, pt_text_bg2, color, CV_FILLED, 8, 0);
                cv::Scalar black_color = CV_RGB(0, 0, 0);
                cv::putText(*show_img, labelstr, pt_text, cv::FONT_HERSHEY_COMPLEX_SMALL, font_size, black_color, 2 * font_size, CV_AA);

                // Display scores
                char score_text[100];
                sprintf(score_text, "P1: %d | P2: %d", score_player1, score_player2);
                cv::putText(*show_img, score_text, cv::Point(10, 30), cv::FONT_HERSHEY_SIMPLEX, 1, CV_RGB(255, 255, 255), 2);
            }
        }
        if (ext_output) {
            fflush(stdout);
        }
    }
    catch (...) {
        cerr << "OpenCV exception: draw_detections_cv_v3() \n";
    }
}
