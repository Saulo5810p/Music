/*
 * Copyright (C) 2007 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.android.music;

import android.database.AbstractCursor;
import android.database.Cursor;

/**
 * Compat replacement for the internal, non-public
 * com.android.internal.database.SortCursor. Merges several cursors into one,
 * ordered by the string value of a shared column, the same way the original
 * AOSP class did. Only used by dead/unreachable code paths kept for source
 * fidelity, so no attempt is made to optimize beyond the original behavior.
 */
public class SortCursorCompat extends AbstractCursor {

    private final Cursor[] mCursors;
    private final String mSortColumn;
    private final int[] mSortColumnIndex;
    private int[] mOrder;

    public SortCursorCompat(Cursor[] cursors, String sortColumn) {
        mCursors = cursors;
        mSortColumn = sortColumn;
        mSortColumnIndex = new int[cursors.length];
        for (int i = 0; i < cursors.length; i++) {
            mSortColumnIndex[i] = cursors[i].getColumnIndex(sortColumn);
            cursors[i].moveToFirst();
        }
        buildOrder();
    }

    private void buildOrder() {
        int total = 0;
        for (Cursor c : mCursors) {
            total += c.getCount();
        }
        // Encode each row as (cursorIndex << 32) | rowIndex, then sort by
        // the sort column's string value.
        final long[] rows = new long[total];
        int pos = 0;
        for (int ci = 0; ci < mCursors.length; ci++) {
            Cursor c = mCursors[ci];
            int count = c.getCount();
            for (int ri = 0; ri < count; ri++) {
                rows[pos++] = (((long) ci) << 32) | (ri & 0xffffffffL);
            }
        }
        Integer[] idx = new Integer[total];
        for (int i = 0; i < total; i++) idx[i] = i;
        java.util.Arrays.sort(idx, (a, b) -> {
            String sa = valueAt(rows[a]);
            String sb = valueAt(rows[b]);
            if (sa == null) return sb == null ? 0 : -1;
            if (sb == null) return 1;
            return sa.compareToIgnoreCase(sb);
        });
        mOrder = new int[total];
        for (int i = 0; i < total; i++) mOrder[i] = idx[i];
        mOrderedRows = rows;
    }

    private long[] mOrderedRows;

    private String valueAt(long encoded) {
        int ci = (int) (encoded >>> 32);
        int ri = (int) encoded;
        Cursor c = mCursors[ci];
        int savedPos = c.getPosition();
        c.moveToPosition(ri);
        String value = mSortColumnIndex[ci] >= 0 ? c.getString(mSortColumnIndex[ci]) : null;
        c.moveToPosition(savedPos);
        return value;
    }

    private Cursor currentCursor() {
        long encoded = mOrderedRows[mOrder[getPosition()]];
        int ci = (int) (encoded >>> 32);
        int ri = (int) encoded;
        Cursor c = mCursors[ci];
        c.moveToPosition(ri);
        return c;
    }

    @Override
    public int getCount() {
        return mOrderedRows == null ? 0 : mOrderedRows.length;
    }

    @Override
    public String[] getColumnNames() {
        return mCursors.length > 0 ? mCursors[0].getColumnNames() : new String[0];
    }

    @Override
    public String getString(int column) {
        return currentCursor().getString(column);
    }

    @Override
    public short getShort(int column) {
        return currentCursor().getShort(column);
    }

    @Override
    public int getInt(int column) {
        return currentCursor().getInt(column);
    }

    @Override
    public long getLong(int column) {
        return currentCursor().getLong(column);
    }

    @Override
    public float getFloat(int column) {
        return currentCursor().getFloat(column);
    }

    @Override
    public double getDouble(int column) {
        return currentCursor().getDouble(column);
    }

    @Override
    public boolean isNull(int column) {
        return currentCursor().isNull(column);
    }
}
