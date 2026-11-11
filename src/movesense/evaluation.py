"""MOT evaluation metrics module (MOTA, Precision, Recall, ID Switches)."""

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment

from movesense.tracker import calculate_iou


def evaluate_tracking(
    gt_df: pd.DataFrame,
    pred_df: pd.DataFrame,
    iou_threshold: float = 0.5,
) -> dict:
    """Evaluate predicted tracking trajectories against ground truth.

    Uses the Hungarian algorithm (linear_sum_assignment) to perform optimal
    bipartite matching per frame based on IoU overlap.

    Parameters
    ----------
    gt_df : pd.DataFrame
        Ground-truth DataFrame with columns: frame, id, x, y, w, h.
    pred_df : pd.DataFrame
        Tracker output DataFrame with columns: frame, id, x, y, w, h.
    iou_threshold : float, default 0.5
        Minimum IoU overlap to consider a predicted box matched to ground truth.

    Returns
    -------
    dict
        Standard MOT metrics including mota, precision, recall, tp, fp, fn, id_switches.
    """
    gt_id_col = "track_id" if "track_id" in gt_df.columns else "id"
    pred_id_col = "track_id" if "track_id" in pred_df.columns else "id"

    gt_by_frame = {f: group for f, group in gt_df.groupby("frame")}
    pred_by_frame = {f: group for f, group in pred_df.groupby("frame")}
    all_frames = sorted(set(gt_by_frame.keys()).union(set(pred_by_frame.keys())))

    total_gt = 0
    tp = 0
    fp = 0
    fn = 0
    id_switches = 0
    last_matched_pred_id: dict[int, int] = {}

    for frame in all_frames:
        gts = gt_by_frame.get(frame)
        preds = pred_by_frame.get(frame)

        n_gt = len(gts) if gts is not None else 0
        n_pred = len(preds) if preds is not None else 0
        total_gt += n_gt

        if n_gt == 0:
            fp += n_pred
            continue
        if n_pred == 0:
            fn += n_gt
            continue

        # Constrói matriz de IoU entre cada GT (linhas) e Predição (colunas)
        gt_boxes = list(zip(gts["x"], gts["y"], gts["w"], gts["h"]))
        pred_boxes = list(zip(preds["x"], preds["y"], preds["w"], preds["h"]))
        gt_ids = gts[gt_id_col].astype(int).tolist()
        pred_ids = preds[pred_id_col].astype(int).tolist()

        iou_matrix = np.zeros((n_gt, n_pred), dtype=float)
        for i, g_box in enumerate(gt_boxes):
            for j, p_box in enumerate(pred_boxes):
                iou_matrix[i, j] = calculate_iou(g_box, p_box)

        # Algoritmo Húngaro minimiza custo -> maximiza IoU usando sinal negativo
        row_ind, col_ind = linear_sum_assignment(-iou_matrix)

        matched_gts = 0
        for r, c in zip(row_ind, col_ind):
            if iou_matrix[r, c] >= iou_threshold:
                matched_gts += 1
                tp += 1

                gt_id = gt_ids[r]
                pred_id = pred_ids[c]
                # Verifica se houve troca de identidade (ID Switch) em relação ao frame anterior
                if gt_id in last_matched_pred_id and last_matched_pred_id[gt_id] != pred_id:
                    id_switches += 1
                last_matched_pred_id[gt_id] = pred_id

        fn += n_gt - matched_gts
        fp += n_pred - matched_gts

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    mota = 1.0 - (fn + fp + id_switches) / total_gt if total_gt > 0 else 0.0

    return {
        "mota": float(mota),
        "precision": float(precision),
        "recall": float(recall),
        "true_positives": int(tp),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "id_switches": int(id_switches),
        "total_gt": int(total_gt),
    }