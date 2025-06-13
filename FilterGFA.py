import os
from collections import defaultdict

def filter_gfa(infile, outfile, min_len, max_len):
    # --- 1) FIRST PASS: build `remove` set using true lengths (incl. LN:i:)
    remove = set()
    with open(infile) as fh:
        for line in fh:
            if not line.startswith('S\t'):
                continue
            cols = line.rstrip('\n').split('\t')
            seg_id, seq = cols[1], cols[2]
            if seq == '*':
                # find LN tag if present
                ln_tags = [t for t in cols[3:] if t.startswith('LN:i:')]
                length = int(ln_tags[0].split(':')[2]) if ln_tags else 0
            else:
                length = len(seq)
            if min_len <= length <= max_len:
                remove.add(seg_id)

    # --- 2) SECOND PASS: rewrite, preserving orientations, delimiters, overlaps
    incoming = defaultdict(list)
    outgoing = defaultdict(list)
    bridged = False

    with open(infile) as fh, open(outfile, 'w') as out:
        for line in fh:
            cols = line.rstrip('\n').split('\t')
            typ = cols[0]

            if typ == 'H':
                out.write(line)

            elif typ == 'S':
                # write only kept segments
                if cols[1] not in remove:
                    out.write(line)

            elif typ == 'L':
                _, frm, f_or, to, t_or, ovl = cols[:6]
                if frm in remove and to not in remove:
                    incoming[to].append((frm, f_or, ovl))
                elif to in remove and frm not in remove:
                    outgoing[frm].append((to, t_or, ovl))
                elif frm not in remove and to not in remove:
                    out.write(line)

            elif typ == 'P':
                # once, emit new bridges preserving orientation & overlap
                if not bridged:
                    for rem in remove & incoming.keys() & outgoing.keys():
                        for (p, p_or, o1) in incoming[rem]:
                            for (n, n_or, o2) in outgoing[rem]:
                                # pick a sensible overlap (e.g. '*' if both are '*')
                                new_ovl = '*' if o1 == '*' and o2 == '*' else o1
                                out.write(f"L\t{p}\t{p_or}\t{n}\t{n_or}\t{new_ovl}\n")
                    bridged = True

                # now filter the path itself
                path_name, seg_field, ovl_field = cols[1], cols[2], cols[3]
                # detect whether this is link-based (,) or jump-based (;)
                delim = ';' if ';' in seg_field else ','
                kept = [
                    seg for seg in seg_field.split(delim)
                    if seg[:-1] not in remove  # seg[-1] is '+' or '-'
                ]
                cols[2] = delim.join(kept)
                # leave cols[3] (the overlaps field, often ‘*’) intact
                out.write('\t'.join(cols) + '\n')

            else:
                # pass through any other records (J, C, W, tags…)
                out.write(line)


filter_gfa("example_chr12.gfa", "chr12_Output.gfa", 5,5)

